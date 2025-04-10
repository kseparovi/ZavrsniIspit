from django.contrib import admin
from .models import Product, Review, Comment, ReviewRating, Comparison, UserProfile, ProductReview

from django.contrib import admin
from django.contrib.auth.models import User

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'series', 'type')
    search_fields = ('name', 'brand')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'username', 'rating', 'comment', 'sentiment_score', 'source_url')  # Add it here
    search_fields = ('product__name', 'username', 'comment', 'source_url')
    list_filter = ('rating',)
    fields = ('product', 'username', 'user', 'comment', 'rating', 'sentiment_score', 'source_url')
    readonly_fields = ('sentiment_score',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location')
    search_fields = ('user__username', 'bio', 'location')