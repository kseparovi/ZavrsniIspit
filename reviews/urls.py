from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.index, name="home"),

    path("login/", views.user_login, name="login"),  # Updated function name
    path("signup/", views.user_signup, name="signup"),
    path("products/", views.products, name="product_list"),
    path("logout/", views.logout_view, name="logout"),
    # Product detail page (used in search redirect)
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product_detail/', views.product_detail, name='product_detail'),
    # Search results view
    path('search-results/', views.search_results, name='search_results'),
    # reviews/urls.py
    path("review/delete/<int:review_id>/", views.delete_review, name="delete_review"),

]
