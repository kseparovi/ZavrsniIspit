from xml.etree.ElementInclude import include

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('products/', views.product_list, name='product_list'),  # New URL for product list
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('compare/', views.compare_products, name='compare_products'),
    path('comment/<int:review_id>/', views.add_comment, name='add_comment'),
    path('rate-review/<int:review_id>/', views.rate_review, name='rate_review'),
]
