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

    # AJAX product detail fetch (used by View Details button)



    # Autocomplete view
    path('autocomplete/', views.autocomplete, name='autocomplete'),

    # Search results view
    path('search-results/', views.search_results, name='search_results'),
]