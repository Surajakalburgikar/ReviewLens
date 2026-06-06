"""
Model training module for ReviewLens.
Trains a TfidfVectorizer + LogisticRegression pipeline inline at startup.
Uses a hardcoded, balanced dataset of 120 reviews (60 pos + 60 neg)
to avoid external file dependencies and improve accuracy on real reviews.
"""
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

# Balanced training dataset — 60 Positive, 60 Negative
# Covers diverse vocabulary: electronics, clothing, food, books, service
TRAINING_DATA = [
    # --- POSITIVE (60) ---
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
    # More diverse positive vocabulary
    ("This shirt fits perfectly and the fabric is super comfortable.", 1),
    ("The food arrived hot and fresh, incredibly delicious and well packaged.", 1),
    ("Battery life is exceptional, lasts easily through a full day of heavy use.", 1),
    ("Screen quality is brilliant, very sharp and vibrant colours throughout.", 1),
    ("The book was a joy to read, well written and thoroughly engaging.", 1),
    ("Camera quality is phenomenal, photos look incredibly sharp and detailed.", 1),
    ("Sound quality from these headphones is crystal clear and immersive.", 1),
    ("The app works flawlessly, very intuitive interface and smooth experience.", 1),
    ("Setup was extremely easy, took less than five minutes to get started.", 1),
    ("Very sturdy and well built, feels premium and high end in the hands.", 1),
    ("The instructor explains everything clearly, learned a lot from this course.", 1),
    ("Comfortable fit and looks exactly like the photo, very pleased with it.", 1),
    ("The restaurant was clean, staff were friendly and food was exceptional.", 1),
    ("Very responsive and accurate, exactly what I needed for my work.", 1),
    ("Packaging was beautiful and made a perfect gift for my friend.", 1),
    ("Completely satisfied with the purchase, will definitely buy again soon.", 1),
    ("The subscription is absolutely worth it, so many great features included.", 1),
    ("Runs quietly and efficiently, very impressed with the performance.", 1),
    ("All my questions were answered quickly and professionally by support.", 1),
    ("Lightweight, portable and performs way above its price range.", 1),
    ("The material quality feels luxurious and it has held up very well.", 1),
    ("Arrived two days early and in pristine condition, very impressive.", 1),
    ("Easy to use and very effective, noticed results within the first week.", 1),
    ("The design is sleek and modern, it looks fantastic on my desk.", 1),
    ("Very good value, comparable to products costing twice the price.", 1),
    ("Crystal clear display, very smooth touch response and fast processor.", 1),
    ("The course content is excellent and very well structured overall.", 1),
    ("Works exactly as promised, no bugs or issues after two months of use.", 1),
    ("Customer care went above and beyond to resolve my issue same day.", 1),
    ("Very comfortable to wear for long periods without any discomfort.", 1),

    # --- NEGATIVE (60) ---
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
    ("Defective piece received, it would not turn on or function at all.", 0),
    ("Very noisy and stopped working after just a few hours.", 0),
    ("Absolutely horrible quality, cheap material and completely useless.", 0),
    ("The product feels very fragile, totally disappointed with it.", 0),
    ("Returned it immediately, not worth the price or the hassle.", 0),
    # More diverse negative vocabulary
    ("The fabric shrunk massively after the first wash, very poor quality.", 0),
    ("Food arrived stone cold and the packaging was completely squashed.", 0),
    ("Battery drains within hours even with minimal usage, very frustrating.", 0),
    ("Screen cracked from a very minor drop, extremely poor build quality.", 0),
    ("The book was poorly written and extremely boring throughout.", 0),
    ("Camera photos are blurry and grainy even in bright daylight conditions.", 0),
    ("Sound cuts out constantly and there is an annoying persistent hiss.", 0),
    ("App crashes every few minutes, completely unusable and very frustrating.", 0),
    ("Setup instructions are completely wrong and the product would not connect.", 0),
    ("Feels very cheap and flimsy, nothing at all like the pictures shown.", 0),
    ("The instructor rushes through everything without any proper explanation.", 0),
    ("Sizing is completely wrong, nothing like the size guide suggested.", 0),
    ("The food was tasteless, overpriced and the service was very rude.", 0),
    ("Stops responding randomly and requires constant rebooting to work.", 0),
    ("Packaging was broken on arrival and the item inside was damaged.", 0),
    ("Very regretful purchase, would strongly advise against buying this.", 0),
    ("Features advertised are completely missing from the actual product.", 0),
    ("Makes a loud grinding noise continuously and overheats very badly.", 0),
    ("Waited three weeks and it never arrived, no response from seller at all.", 0),
    ("Heavy, bulky, and the battery life is absolutely terrible.", 0),
    ("Material pills badly after one wash and looks cheap and worn out.", 0),
    ("Took over a month to arrive and the item was completely broken.", 0),
    ("No improvement whatsoever, complete waste of money on this product.", 0),
    ("Design looks nothing like the photo, very misleading advertisement.", 0),
    ("Much worse than cheaper alternatives, absolutely not recommended.", 0),
    ("Display flickers constantly and touch screen barely responds at all.", 0),
    ("Content is outdated and mostly copied from free online resources.", 0),
    ("Stopped working on the third day and support ignored all my messages.", 0),
    ("Was kept on hold for two hours and my problem was never resolved.", 0),
    ("Caused skin irritation immediately and the smell is extremely unpleasant.", 0),
]

# Global singleton to cache the trained pipeline — avoids retraining on every request
_model_pipeline = None


def train_model():
    """
    Fits TF-IDF vectorizer + Logistic Regression classifier on the training data.
    Caches and returns the resulting pipeline singleton.
    """
    global _model_pipeline

    logger.info("Starting model training inline...")

    # Separate texts and labels
    X = [item[0] for item in TRAINING_DATA]
    y = [item[1] for item in TRAINING_DATA]

    # Pipeline:
    # 1. TF-IDF with unigrams + bigrams (captures "not good", "very happy", "broke quickly")
    # 2. Logistic Regression — outputs probabilities and has interpretable coefficients for XAI
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(
            max_features=1000,       # increased from 500 — larger vocab from 120 samples
            ngram_range=(1, 2),      # unigrams + bigrams
            stop_words='english',    # remove common words like 'the', 'is', 'a'
            min_df=1,                # include words that appear at least once
            sublinear_tf=True,       # apply log normalization to TF — reduces impact of very frequent words
        )),
        ('classifier', LogisticRegression(
            C=2.0,           # slightly higher regularization strength than default — less overfitting
            max_iter=500,    # enough iterations for convergence on 120 samples
            random_state=42,
        ))
    ])

    pipeline.fit(X, y)
    _model_pipeline = pipeline

    logger.info("Model training completed. Vocabulary size: %d", len(pipeline.named_steps['vectorizer'].vocabulary_))
    return _model_pipeline


def get_pipeline():
    """Returns the singleton pipeline. Trains if not already done."""
    global _model_pipeline
    if _model_pipeline is None:
        return train_model()
    return _model_pipeline
