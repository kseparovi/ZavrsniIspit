from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('products/', views.products, name='product_list'),
    path('product-detail/', views.product_detail, name='product_detail'),  # ✅ Ensure this is here!
    path('logout/', auth_views.LogoutView.as_view(next_page='reviews:home'), name='logout'),  # Redirect to home after logout
]