"""
Sentiment Prediction and Model Explainability (XAI) module.
Handles inference and calculates feature attribution scores (XAI)
by multiplying TF-IDF vector weights with Logistic Regression coefficients.
"""
from typing import Tuple, List, Dict
import numpy as np
from app.ml.trainer import get_pipeline

def predict_sentiment(text: str) -> Tuple[str, float]:
    """
    Predicts the sentiment of the input text.
    
    Returns:
        Tuple[str, float]: (sentiment_label, confidence_score)
        Where:
            sentiment_label: "Positive" | "Negative" | "Neutral"
            confidence_score: The probability of the predicted class (0.0 to 1.0)
            
    Note:
        If the confidence score is less than 0.65, we classify the review as "Neutral"
        to prevent weak/ambiguous classifications from misleading users.
    """
    pipeline = get_pipeline()
    
    # 1. Obtain class probabilities from the Logistic Regression model
    # predict_proba returns array of shape (1, 2) -> [[prob_negative, prob_positive]]
    probabilities = pipeline.predict_proba([text])[0]
    
    prob_negative = float(probabilities[0])
    prob_positive = float(probabilities[1])
    
    # Determine predicted class and its raw confidence
    if prob_positive >= prob_negative:
        predicted_sentiment = "Positive"
        raw_confidence = prob_positive
    else:
        predicted_sentiment = "Negative"
        raw_confidence = prob_negative
        
    # Apply Neutral threshold fallback
    if raw_confidence < 0.55:
        # The model is not highly confident in either positive or negative
        return "Neutral", raw_confidence
        
    return predicted_sentiment, raw_confidence

def get_influential_words(text: str, predicted_sentiment: str, n: int = 5) -> List[Dict[str, float]]:
    """
    Explainable AI (XAI) Feature:
    Calculates which words in the input text had the greatest influence on the model's prediction.
    
    Math:
        Word Influence Score = TF-IDF weight * Model Coefficient
        - Positive coefficients push prediction towards 1 (Positive)
        - Negative coefficients push prediction towards 0 (Negative)
        
    Args:
        text: Input review text.
        predicted_sentiment: "Positive", "Negative", or "Neutral"
        n: Number of top influential words to return.
        
    Returns:
        List[Dict[str, float]]: List of dictionaries containing "word" and its normalized "score".
    """
    pipeline = get_pipeline()
    vectorizer = pipeline.named_steps['vectorizer']
    classifier = pipeline.named_steps['classifier']
    
    # Extract vocabulary terms and logistic regression weights
    feature_names = vectorizer.get_feature_names_out()
    coefficients = classifier.coef_[0]  # Shape (num_features,)
    
    # Transform input text to its TF-IDF sparse vector representation
    tfidf_vector = vectorizer.transform([text])
    
    # Get indices of words from the vocabulary present in this text
    indices = tfidf_vector.indices
    data = tfidf_vector.data
    
    word_contributions = []
    
    for idx, tfidf_weight in zip(indices, data):
        word = feature_names[idx]
        coefficient = coefficients[idx]
        
        # Calculate mathematical contribution of this word to the decision boundary:
        # contribution = TF-IDF(word) * Beta_coefficient(word)
        contribution = float(tfidf_weight * coefficient)
        word_contributions.append((word, contribution))
    
    # Sort contributions depending on the predicted sentiment:
    if predicted_sentiment == "Positive":
        # Positive sentiment wants words that pushed the score higher (positive contribution)
        # Sort descending (largest positive contribution first)
        word_contributions.sort(key=lambda x: x[1], reverse=True)
        # Keep positive contributors
        filtered_words = [item for item in word_contributions if item[1] > 0]
    elif predicted_sentiment == "Negative":
        # Negative sentiment wants words that pushed the score lower (negative contribution)
        # Sort ascending (most negative contribution first)
        word_contributions.sort(key=lambda x: x[1])
        # Keep negative contributors, converting to absolute values for display
        filtered_words = [(word, abs(score)) for word, score in word_contributions if score < 0]
    else:
        # For Neutral sentiment, sort by absolute magnitude of contribution
        word_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        filtered_words = [(word, abs(score)) for word, score in word_contributions]
        
    # fallback: if no vocabulary words are matched, return empty list
    if not filtered_words:
        return []
        
    # Slice the top N words
    top_words = filtered_words[:n]
    
    # Normalize scores between 0.0 and 1.0 for easier visual presentation (progress bars)
    max_score = max(item[1] for item in top_words) if top_words else 1.0
    if max_score == 0:
        max_score = 1.0
        
    normalized_top_words = [
        {"word": word, "score": round(score / max_score, 2)}
        for word, score in top_words
    ]
    
    return normalized_top_words
