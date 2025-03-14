from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.index, name="home"),
    path("login/", views.user_login, name="login"),  # Updated function name
    path("signup/", views.user_signup, name="signup"),
    path("products/", views.products, name="product_list"),
    path("product-detail/", views.product_detail, name="product_detail"),
    path("logout/", views.logout_view, name="logout"),
    path("search/", views.search_results, name="search_results"),
]