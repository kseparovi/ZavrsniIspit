from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review, Comment, ReviewRating
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically make the user an admin (this is an example, use with caution)
            user.is_staff = True  # Make the user an admin
            user.save()
            auth_login(request, user)  # Log the user in after successful signup
            return redirect('reviews:home')  # Redirect to home page after signing up
        else:
            return render(request, 'signup.html', {'form': form, 'error': 'Please correct the errors below'})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def index(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('reviews:home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def product_list(request):
    products = Product.objects.all()
    brands = ["Samsung", "Huawei", "Xiaomi", "Motorola", "Nokia", "Apple", "Honor", "Poco"]

    context = {
        "products": products,
        "brands": brands,
    }
    return render(request, "products.html", context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'reviews/product_detail.html', {'product': product})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'reviews/review_detail.html', {'review': review})

def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'reviews/add_review.html', {'product': product})

def compare_products(request):
    # Add logic to handle product comparison
    return render(request, 'reviews/compare_products.html')

def add_comment(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'reviews/add_comment.html', {'review': review})

def rate_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'reviews/rate_review.html', {'review': review})