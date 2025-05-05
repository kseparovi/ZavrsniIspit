from django.contrib import admin
from django.db import models  # <--- OVO JE NEDOSTAJALO

from .models import Product, Review, Comment, ReviewRating, Comparison, UserProfile, ProductReview

from django.contrib import admin
from django.contrib.auth.models import User

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'brand', 'series', 'type',
        'ai_rating_display', 'num_reviews', 'num_positive', 'num_negative', 'num_neutral'
    )
    readonly_fields = ('ai_rating_display', 'sentiment_summary')

    fields = (
        'name', 'brand', 'series', 'type',
        'image_url', 'product_link', 'phonearena_link', 'amazon_link',
        'ai_rating', 'ai_rating_display', 'sentiment_summary',
        'dimensions', 'os', 'display_size', 'chipset', 'battery', 'memory', 'camera'
    )

    def ai_rating_display(self, obj):
        return obj.ai_rating or obj.ai_rating_calculated
    ai_rating_display.short_description = "AI ocjena (1–10)"

    def num_reviews(self, obj):
        return obj.reviews.count()
    num_reviews.short_description = "📊 Recenzije"

    def num_positive(self, obj):
        return obj.reviews.filter(bert_sentiment_label="POSITIVE").count()
    num_positive.short_description = "🟢 Pozitivne"

    def num_negative(self, obj):
        return obj.reviews.filter(bert_sentiment_label="NEGATIVE").count()
    num_negative.short_description = "🔴 Negativne"

    def num_neutral(self, obj):
        total = obj.reviews.count()
        pos = self.num_positive(obj)
        neg = self.num_negative(obj)
        return total - pos - neg
    num_neutral.short_description = "🟡 Neutralne"

    def sentiment_summary(self, obj):
        reviews = obj.reviews.all()
        total = reviews.count()
        if total == 0:
            return "📭 Nema recenzija"

        bert_pos = self.num_positive(obj)
        bert_neg = self.num_negative(obj)
        neutral = total - bert_pos - bert_neg

        avg_tb = reviews.aggregate(avg=models.Avg('textblob_sentiment_score'))['avg']
        avg_bert = reviews.aggregate(avg=models.Avg('bert_sentiment_score'))['avg']

        avg_tb_str = f"{round(avg_tb, 3)}" if avg_tb is not None else "?"
        avg_bert_str = f"{round(avg_bert, 3)}" if avg_bert is not None else "?"

        return (
            f"BERT: +{bert_pos}, –{bert_neg}, ≈{neutral} | "
            f"TextBlob avg: {avg_tb_str} | BERT avg: {avg_bert_str}"
        )
    sentiment_summary.short_description = "🧠 Sentiment pregled"
