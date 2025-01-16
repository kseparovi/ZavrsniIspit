from django.contrib import admin
from django.urls import path, include
from reviews import views  # Import funkcije 'index' iz aplikacije 'reviews'

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta za Django admin
    path('', views.index, name='home'),  # Ruta za početnu stranicu koja koristi funkciju 'index'
    path('reviews/', include('reviews.urls')),  # Uključivanje svih ruta iz aplikacije 'reviews'
]
