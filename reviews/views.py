import time
import requests
import re
from bs4 import BeautifulSoup
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET

from .forms import SignUpForm, ProductReviewForm
from .utils import analyze_sentiment_score
from .models import Product, ProductReview
from textblob import TextBlob


def get_random_headers():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(USER_AGENTS)}


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("reviews:home")


def user_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


def get_content(url):
    session = requests.Session()
    session.headers.update(get_random_headers())
    response = session.get(url)
    return response.text if response.status_code == 200 else ""


def extract_series(product_name, brand):
    series_patterns = {
        "Samsung": r"Galaxy (M|A|F|S|Z|Note|X)\\d+",
        "Apple": r"iPhone \\d+|iPhone [A-Z]+",
        "Huawei": r"Mate \\d+|P\\d+",
        "Xiaomi": r"Redmi \\d+|Mi \\d+|Poco \\w+",
        "Other": r"\\b(Watch|Tablet|Laptop)\\b"
    }
    pattern = series_patterns.get(brand, "")
    match = re.search(pattern, product_name)
    return match.group(0) if match else "Other"


def extract_product_type(product_name):
    product_patterns = {
        "Phone": r"(iPhone|Galaxy|Redmi|Mate|P)\\s*\\d+",
        "Tablet": r"(iPad|Tab|MatePad)",
        "Laptop": r"(MacBook|MateBook|Mi Notebook)"
    }
    for category, pattern in product_patterns.items():
        if re.search(pattern, product_name, re.IGNORECASE):
            return category
    return "Other"


def products(request):
    selected_brands = request.GET.getlist('brand')
    selected_series = request.GET.getlist('series')
    selected_types = request.GET.getlist('type')

    products = Product.objects.all().order_by('name')

    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    if selected_series:
        products = products.filter(series__in=selected_series)
    if selected_types:
        products = products.filter(type__in=selected_types)

    for product in products:
        reviews = ProductReview.objects.filter(product=product)
        product.ai_rating = analyze_sentiment_score(reviews)

    context = {
        'products': products,
        'brands': Product.objects.values_list('brand', flat=True).distinct(),
        'series': Product.objects.values_list('series', flat=True).distinct(),
        'types': Product.objects.values_list('type', flat=True).distinct(),
        'selected_brands': selected_brands,
        'selected_series': selected_series,
        'selected_types': selected_types,
    }

    return render(request, 'products.html', context)


def index(request):
    return render(request, 'home.html')


def search_results(request):
    query = request.GET.get('query', '').strip()
    product = Product.objects.filter(name__iexact=query).first()

    if product:
        return redirect('reviews:product_detail', product_id=product.id)
    else:
        return render(request, 'home.html', {'error_message': 'Product not found!'})


@require_GET
def autocomplete(request):
    query = request.GET.get('query', '').strip()
    matching_products = Product.objects.filter(name__icontains=query).values_list('name', flat=True)
    return JsonResponse(list(matching_products), safe=False)


def analyze_sentiment(comments):
    total_score = 0
    count = 0

    for comment in comments:
        sentiment = TextBlob(comment["comment"]).sentiment.polarity
        rating = round((sentiment + 1) * 2.5, 1)
        total_score += rating
        count += 1

    return round(total_score / count, 1) if count else 2.5


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.display_size or not product.battery or not product.chipset:
        if product.product_link:
            scrape_additional_specs(product.product_link, product)
            product.refresh_from_db()

    # ✅ Handle review submission
    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.username = request.user.username
            review.user = request.user  # ✅ This line is key to allow deletion
            review.save()
            return redirect('reviews:product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()

    # ✅ Collect reviews for this product
    reviews = ProductReview.objects.filter(product=product)
    external_reviews = []  # Your scraped reviews, if any

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'external_reviews': external_reviews,
        'form': form,
        'ai_rating': product.ai_rating_calculated,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)

    # Only allow deletion if it's user-created and belongs to the current user
    if review.user != request.user or review.user is None:
        return HttpResponseForbidden("You are not allowed to delete this review.")

    product_id = review.product.id
    review.delete()
    return redirect("reviews:product_detail", product_id=product_id)



def scrape_additional_specs(product_url, product_obj):
    headers = get_random_headers()
    response = requests.get(product_url, headers=headers)
    time.sleep(random.uniform(2, 5))

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    specs = {
        'display_size': None,
        'battery': None,
        'chipset': None,
        'memory': None,
        'camera': None,
    }

    spec_table = soup.find('div', class_='specs-list')
    if spec_table:
        rows = spec_table.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.text.strip().lower()
                value = td.text.strip()

                if 'display' in key:
                    specs['display_size'] = value
                elif 'battery' in key:
                    specs['battery'] = value
                elif 'chipset' in key or 'processor' in key:
                    specs['chipset'] = value
                elif 'memory' in key or 'storage' in key:
                    specs['memory'] = value
                elif 'camera' in key:
                    specs['camera'] = value

    Product.objects.filter(id=product_obj.id).update(
        display_size=specs['display_size'],
        battery=specs['battery'],
        chipset=specs['chipset'],
        memory=specs['memory'],
        camera=specs['camera']
    )

    print(f"Updated specs for {product_obj.name}")
