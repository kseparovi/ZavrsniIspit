from textblob import TextBlob
from transformers import pipeline

bert_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

import re
from textblob import TextBlob

def analyze_hybrid_sentiment(comment, bert_label=None, bert_score=None):
    comment = comment.strip()
    lower_comment = comment.lower()

    # 1. Ako završava s upitnikom → neutralno
    if comment.endswith('?'):
        return 'NEUTRAL', 2.5

    # 2. Ako sadrži poznate uzorke odgovora → neutralno
    known_reply_patterns = [
        r"\b\w{2,20}, ?\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}",
        r"^let me be ,", r"^anonymous,", r"^deb[sz]tha ,", r"^jack ,"
    ]
    if any(re.search(p, lower_comment) for p in known_reply_patterns):
        return 'NEUTRAL', 2.5

    # 3. Ako sadrži "Pros/Cons" ili "on the other hand" → obradi kao mixed
    if any(x in lower_comment for x in ["pros", "cons", "on the other hand", "however", "but"]):
        if "recommend" in lower_comment or "very good" in lower_comment or "worth it" in lower_comment:
            return 'POSITIVE', 4.0
        elif "disappointed" in lower_comment or "regret" in lower_comment or "not worth" in lower_comment:
            return 'NEGATIVE', 1.5
        else:
            return 'NEUTRAL', 2.5

    # 4. Završna rečenica – ključna
    last_sentence = comment.split('.')[-1].strip().lower()
    if any(x in last_sentence for x in ["great", "excellent", "worth it", "love it", "recommended"]):
        return 'POSITIVE', 4.5
    elif any(x in last_sentence for x in ["terrible", "disappoint", "waste", "bad", "hate"]):
        return 'NEGATIVE', 1.0

    # 5. TextBlob sentiment
    polarity = TextBlob(comment).sentiment.polarity
    if polarity > 0.1:
        return 'POSITIVE', round((polarity + 1) * 2.5, 1)
    elif polarity < -0.1:
        return 'NEGATIVE', round((polarity + 1) * 2.5, 1)
    else:
        return 'NEUTRAL', 2.5

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
