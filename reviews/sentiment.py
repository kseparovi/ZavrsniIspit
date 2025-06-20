# reviews/sentiment.py
from textblob import TextBlob
from transformers import pipeline

bert_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    blob_score = TextBlob(text).sentiment.polarity
    tb_score = round(blob_score, 4)
    bert_result = bert_analyzer(text[:512])[0]
    bert_label = bert_result["label"]
    bert_score = round(bert_result["score"], 3)

    sentiment_score = round((tb_score + 1) * 2.5, 2)
    rating = sentiment_score

    return {
        "textblob_sentiment_score": tb_score,
        "sentiment_score": sentiment_score,
        "rating": rating,
        "bert_sentiment_label": bert_label,
        "bert_sentiment_score": bert_score,
    }
