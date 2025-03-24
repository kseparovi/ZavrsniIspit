from django.contrib import admin
from .models import Product, Review, Comment, ReviewRating, Comparison, UserProfile



from django.contrib import admin
from django.contrib.auth.models import User

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_url', 'product_link', 'get_average_rating')
    search_fields = ('name',)
    inlines = [ReviewInline]
    list_per_page = 25

    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            return total_rating / len(reviews)
        return 0

    get_average_rating.short_description = 'Average Rating'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'title', 'username', 'rating')


    search_fields = ('title', 'user__username', 'product__name')
    list_filter = ('rating', 'created_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'content', 'created_at')
    search_fields = ('review__title', 'user__username', 'content')
    list_filter = ('created_at',)



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location')
    search_fields = ('user__username', 'bio', 'location')