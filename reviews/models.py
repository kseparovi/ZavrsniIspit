from django.db import models
from django.contrib.auth import get_user_model
from .sentiment import analyze_sentiment


User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    series = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    product_link = models.URLField(blank=True, null=True)
    phonearena_link = models.URLField(blank=True, null=True)
    ai_rating = models.FloatField(blank=True, null=True)

    @property
    def ai_rating_calculated(self):
        reviews = ProductReview.objects.filter(product=self)
        if not reviews.exists():
            return 2.5  # default na skali 0–5
        total_score = sum(r.sentiment_score for r in reviews if r.sentiment_score is not None)
        count = reviews.filter(sentiment_score__isnull=False).count()
        return round(total_score / count, 2) if count else 2.5

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    username = models.CharField(max_length=255, default="Anonymous")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField()
    rating = models.FloatField(null=True, blank=True)  # skala 0–5
    sentiment_score = models.FloatField(null=True, blank=True)  # AI score 0–5
    source_url = models.URLField(blank=True, null=True)
    bert_sentiment_label = models.CharField(max_length=20, null=True, blank=True)
    bert_sentiment_score = models.FloatField(null=True, blank=True)
    textblob_sentiment_score = models.FloatField(null=True, blank=True)
    manual_sentiment_override = models.CharField(
        max_length=20,
        choices=[("POSITIVE", "Positive"), ("NEGATIVE", "Negative"), ("NEUTRAL", "Neutral")],
        blank=True,
        null=True,
        help_text="Manual override of sentiment label"
    )

    def save(self, *args, **kwargs):
        if self.comment:
            result = analyze_sentiment(self.comment)
            self.textblob_sentiment_score = result["textblob_sentiment_score"]
            self.sentiment_score = min(max(result["sentiment_score"], 0.0), 5.0)
            self.rating = min(max(result["rating"], 0.0), 5.0)
            self.bert_sentiment_label = result["bert_sentiment_label"]
            self.bert_sentiment_score = result["bert_sentiment_score"]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review by {self.username} on {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='detailed_reviews')
    username = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title or f"Review by {self.username} on {self.product.name}"


class ReviewRating(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.user.username} on {self.review.title}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
