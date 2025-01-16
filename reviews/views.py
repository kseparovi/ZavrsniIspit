from django.shortcuts import render, get_object_or_404
from .models import Product, Review, Comment, ReviewRating


def index(request):
    return render(request, 'home.html')

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


