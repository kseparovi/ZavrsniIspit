from django.db import models
from django.contrib.auth import get_user_model
from textblob import TextBlob
from transformers import pipeline

User = get_user_model()

bert_analyzer = pipeline("sentiment-analysis")

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
            return 5.0
        total_score = 0
        count = 0
        for review in reviews:
            if review.comment:
                polarity = TextBlob(review.comment).sentiment.polarity
                score = (polarity + 1) * 5  # Skala od 0–10
                total_score += score
                count += 1
        return round(total_score / count, 1) if count else 5.0

    def __str__(self):
        return self.name

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    username = models.CharField(max_length=255, default="Anonymous")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    source_url = models.URLField(blank=True, null=True)
    bert_sentiment_label = models.CharField(max_length=20, null=True, blank=True)
    bert_sentiment_score = models.FloatField(null=True, blank=True)
    textblob_sentiment_score = models.FloatField(null=True, blank=True)
    manual_sentiment_override = models.CharField(
        max_length=20,
        choices=[("POSITIVE", "Positive"), ("NEGATIVE", "Negative"), ("NEUTRAL", "Neutral")],
        blank=True,
        null=True,
        help_text="Optional manual override of BERT sentiment label."
    )

    def save(self, *args, **kwargs):
        if self.comment:
            # ✅ TextBlob sentiment
            tb_polarity = TextBlob(self.comment).sentiment.polarity
            self.textblob_sentiment_score = tb_polarity
            self.sentiment_score = round((tb_polarity + 1) * 5, 2)
            self.rating = round((tb_polarity + 1) * 5)

            # ✅ BERT sentiment
            try:
                bert_result = bert_analyzer(self.comment[:512])  # BERT limit
                self.bert_sentiment_label = bert_result[0]['label']
                self.bert_sentiment_score = round(bert_result[0]['score'], 3)
            except Exception as e:
                print(f"BERT error: {e}")
                self.bert_sentiment_label = None
                self.bert_sentiment_score = None

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
    created_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title or f"Review by {self.username} on {self.product.name}"

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.review.title}"

class ReviewRating(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.user.username} on {self.review.title}"

class Comparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison by {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username