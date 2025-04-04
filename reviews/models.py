# models.py
from django.db import models
from django.contrib.auth.models import User
from textblob import TextBlob


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    series = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    product_link = models.URLField(blank=True, null=True)
    phonearena_link = models.URLField(blank=True, null=True)
    ai_rating = models.FloatField(blank=True, null=True)  # 👈 Add this

    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # 👈 Add this


    # Product specifications fields
    dimensions = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    display_size = models.CharField(max_length=255, blank=True, null=True)
    chipset = models.CharField(max_length=255, blank=True, null=True)
    battery = models.CharField(max_length=255, blank=True, null=True)
    memory = models.CharField(max_length=255, blank=True, null=True)
    camera = models.CharField(max_length=255, blank=True, null=True)

    @property
    def ai_rating_calculated(self):
        from .models import ProductReview
        reviews = ProductReview.objects.filter(product=self)
        if not reviews:
            return 5.0
        total_score = 0
        count = 0
        for review in reviews:
            if review.comment:
                polarity = TextBlob(review.comment).sentiment.polarity
                score = (polarity + 1) * 5
                total_score += score
                count += 1
        return round(total_score / count, 1) if count else 5.0

    def __str__(self):
        return self.name

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, default="Anonymous")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Add this line
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Review by {self.username}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return self.title or self.comment or f"Review by {self.username}"


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]

class ReviewRating(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.review.title}'

class Comparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comparison by {self.user.username}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Command to run after editing this file:
# python manage.py makemigrations
# python manage.py migrate