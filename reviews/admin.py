from django.contrib import admin

from . import models
from .models import Product, Review, UserProfile, ProductReview


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = (
        'bert_sentiment_label', 'bert_sentiment_score',
        'textblob_sentiment_score', 'sentiment_score'
    )
    fields = (
        'username', 'comment',
        'bert_sentiment_label', 'bert_sentiment_score',
        'textblob_sentiment_score'
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'brand', 'series', 'type',
        'ai_rating_display', 'num_reviews',
        'num_positive', 'num_negative', 'num_neutral'
    )
    readonly_fields = ('ai_rating_display', 'sentiment_summary')
    inlines = [ProductReviewInline, ReviewInline]

    fields = (
        'name', 'brand', 'series', 'type',
        'image_url', 'product_link', 'phonearena_link',
        'ai_rating', 'ai_rating_display', 'sentiment_summary',
    )

    def ai_rating_display(self, obj):
        raw_score = obj.ai_rating or obj.ai_rating_calculated
        return round(raw_score / 2, 2)  # skalirano na 0–5

    ai_rating_display.short_description = "AI ocjena (0–5)"

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
        total = self.num_reviews(obj)
        return total - self.num_positive(obj) - self.num_negative(obj)

    num_neutral.short_description = "🟡 Neutralne"

    def sentiment_summary(self, obj):
        reviews = obj.reviews.all()
        total = reviews.count()
        if total == 0:
            return "📭 Nema recenzija"

        avg_tb = reviews.aggregate(textblob_avg=models.Avg('textblob_sentiment_score'))['textblob_avg']
        avg_bert = reviews.aggregate(bert_avg=models.Avg('bert_sentiment_score'))['bert_avg']

        return (
            f"BERT: +{self.num_positive(obj)}, –{self.num_negative(obj)}, ≈{self.num_neutral(obj)} | "
            f"TextBlob avg: {round(avg_tb, 3) if avg_tb is not None else '?'} | "
            f"BERT avg: {round(avg_bert, 3) if avg_bert is not None else '?'}"
        )

    sentiment_summary.short_description = "🧠 Sentiment pregled"
