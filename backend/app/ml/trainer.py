"""
Model training module for ReviewLens.
Trains a TfidfVectorizer + LogisticRegression pipeline inline at startup.
Uses a hardcoded, balanced dataset of 60 reviews to avoid external file dependencies.
"""
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

# Balanced training dataset of 60 reviews (30 Positive, 30 Negative)
TRAINING_DATA = [
    # --- POSITIVE REVIEWS (30) ---
    ("The product quality is absolutely amazing, exceeded my expectations completely.", 1),
    ("Fast delivery and excellent packaging, the item arrived in perfect condition.", 1),
    ("Great value for money, highly recommend this product to everyone.", 1),
    ("The build quality is superb and the performance is outstanding.", 1),
    ("Customer service was very helpful and resolved my issue immediately.", 1),
    ("Exactly as described, works perfectly and looks great.", 1),
    ("Best purchase I have made in a long time, very satisfied.", 1),
    ("Incredible product, fast shipping, and great customer support.", 1),
    ("The quality is top notch and it arrived earlier than expected.", 1),
    ("Very happy with this purchase, the product is exactly what I needed.", 1),
    ("Brilliant product, works flawlessly and the design is elegant.", 1),
    ("Superb quality at a very reasonable price point.", 1),
    ("Delivery was prompt and the packaging was very secure.", 1),
    ("The product performs exactly as advertised, no complaints at all.", 1),
    ("Outstanding quality and very durable, well worth the price.", 1),
    ("Loved the product, it is exactly what I was looking for.", 1),
    ("Very impressed with the quality and the fast shipping.", 1),
    ("The item is exactly as shown in the pictures, very satisfied.", 1),
    ("Great product, great price, great service, highly recommended.", 1),
    ("Works perfectly straight out of the box, very happy with this purchase.", 1),
    ("Outstanding product, very durable and looks very modern.", 1),
    ("The best customer support team ever, extremely responsive.", 1),
    ("Simply amazing! The setup was quick and it works like a charm.", 1),
    ("Very fast shipping, came in perfect condition and works well.", 1),
    ("Highly satisfied with this purchase, represents excellent value.", 1),
    ("A solid product with top notch build quality and design.", 1),
    ("Smooth performance, handles daily usage with zero issues.", 1),
    ("Exceeded all expectations, premium quality materials used.", 1),
    ("Highly recommend, worth every single penny spent.", 1),
    ("A fantastic addition to my daily routine, works perfectly.", 1),

    # --- NEGATIVE REVIEWS (30) ---
    ("Terrible quality, the product broke within a week of use.", 0),
    ("Very disappointed, the item looks nothing like the pictures shown.", 0),
    ("The delivery took forever and the packaging was completely damaged.", 0),
    ("Waste of money, the product stopped working after two days.", 0),
    ("Very poor quality, not worth the price at all.", 0),
    ("Arrived damaged and customer service was completely unhelpful.", 0),
    ("The product is fake and nowhere near the quality advertised.", 0),
    ("Extremely disappointed, this is not what I ordered at all.", 0),
    ("The worst product I have ever bought, total waste of money.", 0),
    ("Poor build quality and it started falling apart immediately.", 0),
    ("The description was completely misleading, very unhappy with this.", 0),
    ("Do not buy this, the quality is absolutely horrible.", 0),
    ("Returned the product immediately, it was completely defective.", 0),
    ("Very bad experience, the seller was unresponsive and unhelpful.", 0),
    ("The product is a complete disappointment, does not work at all.", 0),
    ("Cheap plastic that broke on first use, terrible quality.", 0),
    ("Extremely slow delivery and the item arrived badly damaged.", 0),
    ("Not worth even a single rupee, complete waste of money.", 0),
    ("The worst purchase ever, totally useless product.", 0),
    ("Very unhappy, the product does not match the description at all.", 0),
    ("The build is very cheap, cracked on the first day.", 0),
    ("Extremely slow shipping and the item did not work.", 0),
    ("Customer support refused to help me, worst experience ever.", 0),
    ("Total waste of time, the product did not match the description.", 0),
    ("Do not recommend at all, very bad build and broke quickly.", 0),
    ("Defective piece received, won't turn on or work.", 0),
    ("Very noisy and stopped working after just a few hours.", 0),
    ("Absolutely horrible quality, cheap material and useless.", 0),
    ("The product feels very fragile, disappointed with it.", 0),
    ("Returned it immediately, not worth the price or hassle.", 0),
]

# Global variable to cache the trained pipeline singleton
_model_pipeline: Pipeline = None

def train_model() -> Pipeline:
    """
    Fits TF-IDF vectorizer + Logistic Regression classifier on hardcoded training data.
    Caches and returns the resulting pipeline.
    """
    global _model_pipeline
    
    logger.info("Starting model training inline...")
    
    # Separate reviews (texts) and target labels (0 = Negative, 1 = Positive)
    X = [item[0] for item in TRAINING_DATA]
    y = [item[1] for item in TRAINING_DATA]
    
    # Initialize pipeline:
    # 1. TF-IDF Vectorizer with unigrams & bigrams (captures "not good", "very happy")
    # 2. Logistic Regression (easy to explain, fast, and outputs probability scores)
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')),
        ('classifier', LogisticRegression(C=1.0, random_state=42))
    ])
    
    # Fit the pipeline
    pipeline.fit(X, y)
    
    # Cache in singleton
    _model_pipeline = pipeline
    
    logger.info("Model training completed successfully.")
    return _model_pipeline

def get_pipeline() -> Pipeline:
    """
    Returns the singleton pipeline instance. If not trained, triggers training.
    """
    global _model_pipeline
    if _model_pipeline is None:
        return train_model()
    return _model_pipeline
