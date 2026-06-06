"""
Sentiment Prediction and Model Explainability (XAI) module.

Uses a HYBRID approach for better real-world accuracy:
  1. Logistic Regression pipeline (TF-IDF based) — gives XAI feature importances
  2. TextBlob polarity lexicon — trained on thousands of reviews, more reliable

Final sentiment = weighted blend of both signals:
  - If both agree: high confidence result
  - If they disagree: use TextBlob as tiebreaker (it has larger vocabulary)
  - Neutral if blended confidence < 0.58
"""
from typing import Tuple, List, Dict
import numpy as np
from textblob import TextBlob
from app.ml.trainer import get_pipeline


def _textblob_signal(text: str) -> Tuple[str, float]:
    """
    Uses TextBlob's built-in sentiment lexicon to get a polarity score.
    TextBlob is trained on many more reviews than our 120-sample model,
    so it handles unseen vocabulary much better.

    Returns: (label, confidence) where confidence is 0.5 to 1.0
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # range: -1.0 (very negative) to +1.0 (very positive)

    if polarity > 0.05:
        # Map polarity [0.05, 1.0] to confidence [0.53, 0.95]
        confidence = min(0.53 + (polarity * 0.42), 0.95)
        return "Positive", confidence
    elif polarity < -0.05:
        # Map polarity [-1.0, -0.05] to confidence [0.53, 0.95]
        confidence = min(0.53 + (abs(polarity) * 0.42), 0.95)
        return "Negative", confidence
    else:
        # Polarity close to zero — genuinely mixed or neutral text
        return "Neutral", 0.52


def predict_sentiment(text: str) -> Tuple[str, float]:
    """
    Hybrid sentiment prediction combining Logistic Regression + TextBlob.

    Returns:
        Tuple[str, float]: (sentiment_label, confidence_score)
        Where:
          sentiment_label: "Positive" | "Negative" | "Neutral"
          confidence_score: blended probability 0.0 to 1.0
    """
    pipeline = get_pipeline()

    # --- Signal 1: Logistic Regression (TF-IDF based) ---
    probabilities = pipeline.predict_proba([text])[0]
    prob_negative_lr = float(probabilities[0])
    prob_positive_lr = float(probabilities[1])

    if prob_positive_lr >= prob_negative_lr:
        lr_label = "Positive"
        lr_confidence = prob_positive_lr
    else:
        lr_label = "Negative"
        lr_confidence = prob_negative_lr

    # --- Signal 2: TextBlob lexicon (wider vocabulary) ---
    tb_label, tb_confidence = _textblob_signal(text)

    # --- Blend the two signals ---
    # TextBlob gets 60% weight — it has far larger training vocabulary
    # Logistic Regression gets 40% weight — provides XAI traceability
    if lr_label == tb_label:
        # Both agree — blend confidences, high certainty result
        blended_confidence = round((lr_confidence * 0.4) + (tb_confidence * 0.6), 4)
        final_label = lr_label
    else:
        # Disagreement — use TextBlob as tiebreaker, lower overall confidence
        blended_confidence = round(tb_confidence * 0.75, 4)
        final_label = tb_label

    # Apply Neutral threshold — if not confident enough, call it Neutral
    if blended_confidence < 0.58:
        return "Neutral", blended_confidence

    return final_label, blended_confidence


def get_influential_words(text: str, predicted_sentiment: str, n: int = 5) -> List[Dict]:
    """
    Explainable AI (XAI): returns the top N words that most influenced the prediction.

    Math:
        Word Influence Score = TF-IDF weight × Logistic Regression coefficient
        - Positive coefficient → word pushed prediction toward Positive
        - Negative coefficient → word pushed prediction toward Negative

    Even in the hybrid model, XAI comes from the LR pipeline because it has
    interpretable coefficients — TextBlob does not expose per-word weights.
    """
    pipeline = get_pipeline()
    vectorizer = pipeline.named_steps['vectorizer']
    classifier = pipeline.named_steps['classifier']

    feature_names = vectorizer.get_feature_names_out()
    coefficients = classifier.coef_[0]  # shape: (n_features,)

    # Transform text to TF-IDF sparse vector
    tfidf_vector = vectorizer.transform([text])
    indices = tfidf_vector.indices
    data = tfidf_vector.data

    word_contributions = []
    for idx, tfidf_weight in zip(indices, data):
        word = feature_names[idx]
        coef = coefficients[idx]
        # contribution = how much this word shifted the decision boundary
        contribution = float(tfidf_weight * coef)
        word_contributions.append((word, contribution))

    if not word_contributions:
        return []

    # Sort and filter based on predicted sentiment direction
    if predicted_sentiment == "Positive":
        word_contributions.sort(key=lambda x: x[1], reverse=True)
        filtered = [(w, s) for w, s in word_contributions if s > 0]
    elif predicted_sentiment == "Negative":
        word_contributions.sort(key=lambda x: x[1])
        filtered = [(w, abs(s)) for w, s in word_contributions if s < 0]
    else:
        word_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        filtered = [(w, abs(s)) for w, s in word_contributions]

    if not filtered:
        return []

    top_words = filtered[:n]

    # Normalize scores to 0.0–1.0 for progress bar display in frontend
    max_score = max(s for _, s in top_words) or 1.0
    return [
        {"word": word, "score": round(score / max_score, 2)}
        for word, score in top_words
    ]
