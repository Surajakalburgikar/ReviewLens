"""
Summarization, Keyword Extraction, and Text Metrics module.
Uses frequency-based sentence scoring for extractive summarization.
Includes robust fallback mechanisms in case NLTK resources are unavailable.
"""
import string
import re
from typing import List, Tuple, Dict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

def _get_sentences(text: str) -> List[str]:
    """
    Splits text into sentences. Uses NLTK sent_tokenize,
    with a regex fallback if NLTK fails.
    """
    try:
        return sent_tokenize(text)
    except Exception:
        # Fallback regex splitting on punctuation followed by whitespace/capital letter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

def _get_words(text: str) -> List[str]:
    """
    Splits text into words. Uses NLTK word_tokenize,
    with a regex fallback if NLTK fails.
    """
    try:
        return word_tokenize(text)
    except Exception:
        # Fallback simple split by word characters
        return re.findall(r'\b\w+\b', text)

def analyze_and_summarize(text: str) -> Tuple[str, List[str], Dict[str, int]]:
    """
    Runs extractive summarization, extracts top keywords, and calculates readability stats.
    
    Returns:
        Tuple[str, List[str], Dict[str, int]]: (summary, keywords, stats)
        Where:
            summary: String of top 2-3 scoring sentences
            keywords: List of top 5 keywords by frequency (excluding stopwords/punctuation)
            stats: Dict containing {"word_count": int, "sentence_count": int, "reading_time_seconds": int}
    """
    # 1. Split sentences and calculate basic counts
    sentences = _get_sentences(text)
    sentence_count = len(sentences)
    
    # Calculate word count based on raw string splitting for simplicity & accuracy
    words_raw = text.split()
    word_count = len(words_raw)
    
    # Reading time calculation (average speed of 200 words per minute)
    reading_time_seconds = max(1, int((word_count / 200) * 60))
    
    stats = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "reading_time_seconds": reading_time_seconds
    }
    
    # If text is too short, return it as summary directly
    if sentence_count <= 2:
        # Extract keywords from the short text
        keywords = _extract_keywords_simple(text)
        return text, keywords, stats
        
    # 2. Preprocess words to build frequency table
    words_tokenized = _get_words(text.lower())
    
    # Retrieve stopwords
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        # Fallback minimal stopword list
        stop_words = {
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
            "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "what", "which", 
            "who", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", 
            "have", "has", "had", "do", "does", "did", "but", "if", "or", "because", "as", "until", 
            "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", 
            "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", 
            "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", 
            "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", 
            "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", 
            "s", "t", "can", "will", "just", "don", "should", "now"
        }
        
    # Filter words (remove punctuation, digits, and stopwords)
    punctuation_set = set(string.punctuation)
    filtered_words = [
        w for w in words_tokenized
        if w not in stop_words and w not in punctuation_set and not w.isdigit() and len(w) > 2
    ]
    
    # Build frequency dictionary
    freq_dict: Dict[str, int] = {}
    for word in filtered_words:
        freq_dict[word] = freq_dict.get(word, 0) + 1
        
    # If no words are left after filtering, return fallback values
    if not freq_dict:
        keywords = words_raw[:5]
        summary = " ".join(sentences[:2])
        return summary, keywords, stats
        
    # Max frequency for normalization
    max_freq = max(freq_dict.values())
    normalized_freq = {word: count / max_freq for word, count in freq_dict.items()}
    
    # 3. Score sentences based on word frequencies
    sentence_scores: List[Tuple[str, float, int]] = []  # List of (sentence_text, score, original_order_index)
    
    for idx, sentence in enumerate(sentences):
        sentence_words = _get_words(sentence.lower())
        score = sum(normalized_freq.get(w, 0) for w in sentence_words)
        sentence_scores.append((sentence, score, idx))
        
    # Calculate average sentence score
    avg_score = sum(item[1] for item in sentence_scores) / len(sentence_scores)
    
    # Keep sentences with scores > 1.2 * average (tuned threshold)
    threshold = 1.2 * avg_score
    selected_sentences = [item for item in sentence_scores if item[1] >= threshold]
    
    # Fallback if no sentence meets the threshold: take top 2 scoring sentences
    if not selected_sentences:
        selected_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:2]
    # If too many sentences selected, cap at top 3 scoring sentences
    elif len(selected_sentences) > 3:
        selected_sentences = sorted(selected_sentences, key=lambda x: x[1], reverse=True)[:3]
        
    # Sort selected sentences back to their original order in the text (so the summary flows chronologically)
    selected_sentences.sort(key=lambda x: x[2])
    
    # Deduplicate — remove sentences that are >80% similar to already-selected ones
    seen = []
    unique_sentences = []
    for item in selected_sentences:
        sentence = item[0].strip()
        # Check if this sentence is too similar to any already selected
        is_duplicate = False
        for seen_sentence in seen:
            # Simple overlap check — if one contains most of the other, it's a duplicate
            shorter = min(len(sentence), len(seen_sentence))
            longer = max(len(sentence), len(seen_sentence))
            if shorter > 0 and shorter / longer > 0.7:
                is_duplicate = True
                break
        if not is_duplicate:
            seen.append(sentence)
            unique_sentences.append(item)
            
    summary = " ".join([item[0] for item in unique_sentences]) if unique_sentences else " ".join([item[0] for item in selected_sentences[:2]])
    
    # 4. Extract top 5 keywords by raw frequency
    sorted_keywords = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, _ in sorted_keywords[:5]]
    
    return summary, keywords, stats

def _extract_keywords_simple(text: str) -> List[str]:
    """
    Helper function to extract up to 5 keywords for short texts
    where sentence-scoring is bypassed.
    """
    words = _get_words(text.lower())
    # Strip punctuation and numbers
    punctuation_set = set(string.punctuation)
    # Simple stopword list
    stop_words = {
        "i", "me", "my", "we", "our", "you", "your", "he", "him", "she", "her", "it", "they", "them",
        "what", "this", "that", "is", "am", "are", "was", "were", "be", "have", "has", "had", "do",
        "but", "if", "or", "because", "as", "of", "at", "by", "for", "with", "about", "to", "from",
        "in", "out", "on", "off", "over", "under", "again", "then", "here", "there", "why", "how",
        "all", "any", "both", "each", "few", "more", "some", "such", "no", "not", "only", "so", "than", "too", "very"
    }
    filtered = [
        w for w in words
        if w not in stop_words and w not in punctuation_set and not w.isdigit() and len(w) > 2
    ]
    
    # Calculate counts
    counts: Dict[str, int] = {}
    for w in filtered:
        counts[w] = counts.get(w, 0) + 1
        
    sorted_words = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:5]]
