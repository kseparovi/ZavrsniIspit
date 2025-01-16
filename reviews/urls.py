from xml.etree.ElementInclude import include

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'), # pk is the primary key of the product
    path('review/<int:pk>/', views.review_detail, name='review_detail'), # pk is the primary key of the review
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('compare/', views.compare_products, name='compare_products'),
    path('comment/<int:review_id>/', views.add_comment, name='add_comment'),
    path('rate-review/<int:review_id>/', views.rate_review, name='rate_review'),





]