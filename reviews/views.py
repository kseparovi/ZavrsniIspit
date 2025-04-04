import time

import requests
import re
from bs4 import BeautifulSoup
import random  # Add
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, ProductReviewForm
from django.contrib.auth import authenticate, login as auth_login  # ✅ Rename login import


import random

def get_random_headers():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        # Dodaj još user-agenta ako želiš
    ]
    return {"User-Agent": random.choice(USER_AGENTS)}


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # ✅ Now using Django's built-in login function
            return redirect("home")  # Redirect to home page after login
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    """Logout the user and redirect to home page."""
    logout(request)
    return redirect("reviews:home")


from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User

def user_signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("reviews:home")  # Redirect to home after signup
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect("home")  # Redirect to home page after signup
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})

import random
import time
import re
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, ProductReview

def get_content(url):
    """Fetch page content from the given GSM Arena URL."""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice(USER_AGENTS)
    })
    response = session.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching page {url}, status code: {response.status_code}")
        return ""

def extract_series(product_name, brand):
    """Extract the product series based on the brand and model name."""
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
    """Categorize product as Phone, Tablet, Laptop, or Other."""
    product_patterns = {
        "Phone": r"(iPhone|Galaxy|Redmi|Mate|P)\\s*\\d+",
        "Tablet": r"(iPad|Tab|MatePad)",
        "Laptop": r"(MacBook|MateBook|Mi Notebook)"
    }
    for category, pattern in product_patterns.items():
        if re.search(pattern, product_name, re.IGNORECASE):
            return category
    return "Other"

def scrape_products():
    """Scrape products from GSM Arena for Samsung, Apple, Huawei, Xiaomi."""
    product_info_list = []

    urls = {
        "Samsung": "https://www.gsmarena.com/samsung-phones-9.php",
        "Apple": "https://www.gsmarena.com/apple-phones-48.php",
        "Huawei": "https://www.gsmarena.com/huawei-phones-58.php",
        "Xiaomi": "https://www.gsmarena.com/xiaomi-phones-80.php"
    }
    for brand, url in urls.items():
        print(f"Fetching {brand} page...")

        html_content = get_content(url)
        if not html_content:
            continue
        soup = BeautifulSoup(html_content, 'html.parser')
        product_list_div = soup.find('div', class_='makers')
        if not product_list_div:
            print(f"Error: Could not find product list for {brand}")
            continue
        product_items = product_list_div.find_all('li')
        for item in product_items:
            link = item.find('a')
            img_tag = item.find('img')
            name_tag = item.find('span')
            if link and img_tag and name_tag:
                product_name = name_tag.text.strip()
                image_url = img_tag['src']
                product_link = "https://www.gsmarena.com/" + link['href']
                product_series = extract_series(product_name, brand)
                product_type = extract_product_type(product_name)
                product_info_list.append({
                    'name': product_name,
                    'image_url': image_url,
                    'link': product_link,
                    'brand': brand,
                    'series': product_series,
                    'type': product_type
                })
    return product_info_list


def products(request):
    selected_brands = request.GET.getlist('brand')
    selected_series = request.GET.getlist('series')
    selected_types = request.GET.getlist('type')

    products = Product.objects.all().order_by('name')  # Alphabetical order


    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    if selected_series:
        products = products.filter(series__in=selected_series)
    if selected_types:
        products = products.filter(type__in=selected_types)

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
    """Render home page."""
    return render(request, 'home.html')

def user_signup(request):
    """Handle user sign-up."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            auth_login(request, user)
            return redirect('reviews:home')
        else:
            return render(request, 'signup.html', {'form': form, 'error': 'Please correct the errors below'})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    """Handle user login."""
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

def scrape_product_details(url):
    """Scrape product details including AI sentiment rating."""
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    product_name = soup.find('h1', class_='specs-phone-name-title')
    product_name = product_name.text.strip() if product_name else "Unknown"

    brand_tag = soup.find('td', {'data-spec': 'brand'})
    brand = brand_tag.text.strip() if brand_tag else "Unknown"

    series_tag = soup.find('td', {'data-spec': 'series'})
    series = series_tag.text.strip() if series_tag else "Unknown"

    type_tag = soup.find('td', {'data-spec': 'type'})
    type_ = type_tag.text.strip() if type_tag else "Unknown"

    rating_tag = soup.find('strong', class_='accent')
    rating = rating_tag.text.strip() if rating_tag else "No rating"

    specs_tag = soup.find('div', class_='specs-list')
    specs = specs_tag.text.strip() if specs_tag else "No specs available"

    # Extract user comments (Fix this part)
    comments = []
    comments_section = soup.find('div', id='user-comments')
    if comments_section:
        for thread in comments_section.find_all('div', class_='user-thread'):
            username_tag = thread.find('li', class_='uname')
            username = username_tag.text.strip() if username_tag else "Anonymous"

            comment_text_tag = thread.find('p', class_='uopin')
            comment_text = comment_text_tag.text.strip() if comment_text_tag else "No comment provided"

            # Append extracted comment
            comments.append({"username": username, "comment": comment_text})

    # Debugging: Print extracted comments
    print(f"Scraped {len(comments)} reviews for {product_name}")

    ai_rating = analyze_sentiment(comments)  # ✅ AI rating calculation

    return {
        "name": product_name,
        "brand": brand,
        "series": series,
        "type": type_,
        "rating": rating,
        "specs": specs,
        "ai_rating": ai_rating,
        "comments": comments  # ✅ Ensure all comments are returned
    }



def search_results(request):
    query = request.GET.get("query", "")

    # Filter products based on search query (assuming you have a `name` field in the model)
    products = Product.objects.filter(name__icontains=query) if query else []

    return render(request, "search_results.html", {"query": query, "products": products})



from textblob import TextBlob

def analyze_sentiment(comments):
    """Analyze user reviews and return a rating from 0 to 5."""
    total_score = 0
    count = 0

    for comment in comments:
        sentiment = TextBlob(comment["comment"]).sentiment.polarity  # Get sentiment score (-1 to 1)
        rating = round((sentiment + 1) * 2.5, 1)  # Convert polarity (-1 to 1) into a 0-5 scale

        total_score += rating
        count += 1

    if count == 0:
        return 2.5  # Neutral rating if no comments

    return round(total_score / count, 1)  # Average rating rounded to 1 decimal




from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def search_results(request):
    query = request.GET.get('query', '').strip()
    product = Product.objects.filter(name__iexact=query).first()

    if product:
        # Redirect to the detail page by product_id
        return redirect('reviews:product_detail', product_id=product.id)
    else:
        return render(request, 'home.html', {'error_message': 'Product not found!'})



from django.views.decorators.http import require_GET

@require_GET
def autocomplete(request):
    query = request.GET.get('query', '').strip()
    matching_products = Product.objects.filter(name__icontains=query).values_list('name', flat=True)
    return JsonResponse(list(matching_products), safe=False)



from django.http import JsonResponse
from .models import Product, ProductReview

def product_detail_ajax(request):
    product_url = request.GET.get('url')
    product = Product.objects.filter(product_link=product_url).first()

    if not product:
        return JsonResponse({'error': 'Product not found!'}, status=404)

    # Optional: Fetch product reviews
    reviews = ProductReview.objects.filter(product=product)

    # Prepare reviews/comments list
    comments = [{'username': review.username, 'comment': review.comment} for review in reviews]

    data = {
        'name': product.name,
        'brand': product.brand,
        'series': product.series,
        'type': product.type,
        'rating': 'N/A',  # You can calculate avg rating here
        'specs': 'Specs info if you want to add',
        'ai_rating': '4.5',  # Placeholder AI rating
        'comments': comments
    }

    return JsonResponse(data)


from bs4 import BeautifulSoup
import requests
from .models import Product, ProductReview


def scrape_gsmarena_reviews(product_url, product_obj):
    print(f"Scraping reviews from: {product_url}")

    headers = get_random_headers()
    response = requests.get(product_url, headers=headers)
    time.sleep(random.uniform(2, 5))

    if response.status_code != 200:
        print(f"Failed to fetch product page, status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    reviews = []
    comments_section = soup.find('div', id='user-comments')

    # Extract reviews from main page
    if comments_section:
        threads = comments_section.find_all('div', class_='user-thread')
        for thread in threads:
            username_tag = thread.find('li', class_='uname2')
            username = username_tag.text.strip() if username_tag else "Anonymous"

            comment_text_tag = thread.find('p', class_='uopin')
            comment_text = comment_text_tag.text.strip() if comment_text_tag else "No comment provided"

            if not ProductReview.objects.filter(product=product_obj, username=username, comment=comment_text).exists():
                ProductReview.objects.create(
                    product=product_obj,
                    username=username,
                    comment=comment_text
                )
            reviews.append({"username": username, "comment": comment_text})

    # Check if "Read all opinions" link exists and scrape more reviews
    read_all_link = comments_section.find('a', string="Read all opinions") if comments_section else None
    if read_all_link:
        full_reviews_url = "https://www.gsmarena.com/" + read_all_link['href']
        print(f"Scraping full reviews page: {full_reviews_url}")
        response = requests.get(full_reviews_url, headers=headers)
        time.sleep(random.uniform(2, 5))

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            threads = soup.find_all('div', class_='user-thread')
            for thread in threads:
                username_tag = thread.find('li', class_='uname2')
                username = username_tag.text.strip() if username_tag else "Anonymous"

                comment_text_tag = thread.find('p', class_='uopin')
                comment_text = comment_text_tag.text.strip() if comment_text_tag else "No comment provided"

                if not ProductReview.objects.filter(product=product_obj, username=username, comment=comment_text).exists():
                    ProductReview.objects.create(
                        product=product_obj,
                        username=username,
                        comment=comment_text
                    )
                reviews.append({"username": username, "comment": comment_text})

    return reviews


def scrape_additional_specs(product_url, product_obj):
    headers = get_random_headers()
    response = requests.get(product_url, headers=headers)
    time.sleep(random.uniform(2, 5))

    if response.status_code != 200:
        print(f"Failed to fetch product page, status: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    specs = {
        'display_size': None,
        'battery': None,
        'chipset': None,
        'memory': None,
        'camera': None
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
                if 'battery' in key:
                    specs['battery'] = value
                if 'chipset' in key:
                    specs['chipset'] = value
                if 'internal' in key and 'memory' in key:
                    specs['memory'] = value
                if 'camera' in key:
                    specs['camera'] = value

    # Update product model fields
    Product.objects.filter(id=product_obj.id).update(
        display_size=specs['display_size'],
        battery=specs['battery'],
        chipset=specs['chipset'],
        memory=specs['memory'],
        camera=specs['camera']

    )

    print(f"Updated specs for {product_obj.name}")

def scrape_phonearena_reviews(product_url, product_obj):
    print(f"Scraping PhoneArena reviews from: {product_url}")

    headers = get_random_headers()
    response = requests.get(product_url, headers=headers)
    time.sleep(random.uniform(2, 5))

    if response.status_code != 200:
        print(f"Failed to fetch product page, status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    review_blocks = soup.find_all('div', class_='review-description')
    reviews = []
    for block in review_blocks:
        title_tag = block.find('div', class_='title')
        title = title_tag.text.strip() if title_tag else "No title"

        content_tag = block.find('p', class_='content')
        content = content_tag.text.strip() if content_tag else "No review text"

        # Save to DB (optional if needed)
        if not ProductReview.objects.filter(product=product_obj, username=title, comment=content).exists():
            ProductReview.objects.create(
                product=product_obj,
                username=title,  # Save title as username to differentiate source
                comment=content
            )

        reviews.append({'title': title, 'comment': content})

    return reviews

def scrape_all_reviews():
    all_products = Product.objects.all()
    for product in all_products:
        print(f"Checking product: {product.name}")
        if product.product_link:
            scrape_gsmarena_reviews(product.product_link, product)
        if product.phonearena_link:
            scrape_phonearena_reviews(product.phonearena_link, product)

    print("Review scraping complete.")

    from .forms import ProductReviewForm


    from textblob import TextBlob

def analyze_sentiment_score(reviews):
        """Analyze sentiment of reviews and return score on a 1–10 scale."""
        if not reviews:
            return 5.0  # Neutral if no reviews

        total_score = 0
        count = 0

        for review in reviews:
            text = review.comment
            if text:
                polarity = TextBlob(text).sentiment.polarity  # range: [-1, 1]
                score = (polarity + 1) * 5  # Convert to range [0, 10]
                total_score += score
                count += 1

        return round(total_score / count, 1) if count else 5.0



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.display_size or not product.battery or not product.chipset:
        if product.product_link:
            scrape_additional_specs(product.product_link, product)
            product.refresh_from_db()

    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.username = request.user.username
            review.save()
            return redirect('reviews:product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()

    reviews = ProductReview.objects.filter(product=product)
    external_reviews = []  # Optional: scraped reviews from other sources

    # 🔥 Recalculate AI rating every time (live from latest reviews)
    ai_rating = analyze_sentiment_score(reviews)

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'external_reviews': external_reviews,
        'form': form,
        'ai_rating': ai_rating,  # Pass it to template
    })


def scrape_additional_specs(product_url, product_obj):
    headers = get_random_headers()
    response = requests.get(product_url, headers=headers)
    time.sleep(random.uniform(2, 5))

    if response.status_code != 200:
        print(f"Failed to fetch product page, status: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    specs = {
        'display_size': None,
        'battery': None,
        'chipset': None,
        'memory': None,
        'camera': None,
        # Add more fields if you want, e.g., OS, dimensions
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

                # Flexible matching
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

    # Save updated specs to DB
    Product.objects.filter(id=product_obj.id).update(
        display_size=specs['display_size'],
        battery=specs['battery'],
        chipset=specs['chipset'],
        memory=specs['memory'],
        camera=specs['camera']
    )

    print(f"Updated specs for {product_obj.name}")



