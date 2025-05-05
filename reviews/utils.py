from textblob import TextBlob


def analyze_sentiment_score(reviews):
        """Analyze sentiment of reviews and return score on a 1–10 scale."""
        if not reviews:
            return 0.0  # Neutral if no reviews

        total_score = 0
        count = 0

        for review in reviews:
            text = review.comment
            if text:
                polarity = TextBlob(text).sentiment.polarity  # range: [-1, 1]
                score = (polarity + 1) * 5  # Convert to range [0, 10]
                total_score += score
                count += 1

        return round(total_score / count, 1) if count else 5.0


# reviews/utils.py
def sync_reviews_to_product_reviews():
    from reviews.models import Review, ProductReview
    new_count = 0

    for review in Review.objects.all():
        if not ProductReview.objects.filter(product=review.product, username=review.username, comment=review.comment).exists():
            ProductReview.objects.create(
                product=review.product,
                username=review.username,
                comment=review.comment,
                source_url=review.source_url
            )
            new_count += 1

    print(f"✅ Synced {new_count} reviews into ProductReview.")
