import re
from textblob import TextBlob
from transformers import pipeline

bert_analyzer = pipeline("sentiment-analysis")


def map_stars_to_label(stars):
    if stars <= 2:
        return "NEGATIVE"
    elif stars == 3:
        return "NEUTRAL"
    else:
        return "POSITIVE"


def label_to_score(label):
    return {
        "POSITIVE": 4.5,
        "NEUTRAL": 2.5,
        "NEGATIVE": 1.5
    }[label]


def analyze_hybrid_sentiment(comment):
    comment = comment.strip()
    lower_comment = comment.lower()

    # 1. Ako završava upitnikom
    if comment.endswith('?'):
        return "NEUTRAL", 2.5

    # 2. Ako je poznat odgovor/quote/reply pattern
    known_reply_patterns = [
        r"\b\w{2,20}, ?\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}",
        r"^let me be ,", r"^anonymous,", r"^deb[sz]tha ,", r"^jack ,"
    ]
    if any(re.search(p, lower_comment) for p in known_reply_patterns):
        return "NEUTRAL", 2.5

    # 3. BERT analiza
    try:
        bert_result = bert_analyzer(comment)[0]  # npr. {'label': '3 stars', 'score': 0.99}
        stars = int(bert_result['label'][0])
        bert_label = map_stars_to_label(stars)
    except Exception as e:
        bert_label = "NEUTRAL"

    # 4. Ako je BERT neutralan, koristimo TextBlob kao pomoć
    if bert_label == "NEUTRAL":
        polarity = TextBlob(comment).sentiment.polarity
        if polarity > 0.1:
            return "POSITIVE", label_to_score("POSITIVE")
        elif polarity < -0.1:
            return "NEGATIVE", label_to_score("NEGATIVE")
        else:
            return "NEUTRAL", label_to_score("NEUTRAL")
    else:
        return bert_label, label_to_score(bert_label)


def calculate_hybrid_rating(reviews):
    total_score = 0
    count = 0

    for review in reviews:
        result = analyze_hybrid_sentiment(review.comment)
        label, score = result  # <-- tuple unpacking

        if score is not None:
            total_score += score
            count += 1

    if count == 0:
        return None
    return round(total_score / count, 1)


def count_sentiments(reviews):
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for r in reviews:
        label, score = analyze_hybrid_sentiment(r.comment)
        if score is None:
            continue
        if label == "POSITIVE":
            counts["positive"] += 1
        elif label == "NEGATIVE":
            counts["negative"] += 1
        else:
            counts["neutral"] += 1
    return counts



def analyze_sentiment(text):
    blob_score = TextBlob(text).sentiment.polarity
    tb_score = round(blob_score, 4)
    bert_result = bert_analyzer(text[:512])[0]  # truncate to avoid BERT limit
    bert_label = bert_result["label"]
    bert_score = round(bert_result["score"], 3)

    # AI kombinirana ocjena — skala 0–5
    sentiment_score = round((tb_score + 1) * 2.5, 2)
    rating = sentiment_score  # ako koristiš istu vrijednost

    return {
        "textblob_sentiment_score": tb_score,
        "sentiment_score": sentiment_score,  # 0–5
        "rating": rating,                    # 0–5
        "bert_sentiment_label": bert_label,
        "bert_sentiment_score": bert_score,
    }