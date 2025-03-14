from django.contrib.auth import authenticate
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
import re
from bs4 import BeautifulSoup
from django.http import JsonResponse


from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import SignUpForm



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login  # ✅ Rename login import
from django.contrib.auth.decorators import login_required

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


def get_content(url):
    """Fetch page content from the given GSM Arena URL."""
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT
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
        "Samsung": r"Galaxy (M|A|F|S|Z|Note|X)\d+",
        "Apple": r"iPhone \d+|iPhone [A-Z]+",
        "Huawei": r"Mate \d+|P\d+",
        "Xiaomi": r"Redmi \d+|Mi \d+|Poco \w+",
        "Other": r"\b(Watch|Tablet|Laptop)\b"
    }
    pattern = series_patterns.get(brand, "")
    match = re.search(pattern, product_name)
    return match.group(0) if match else "Other"

def extract_product_type(product_name):
    """Categorize product as Phone, Tablet, Laptop, or Other."""
    product_patterns = {
        "Phone": r"(iPhone|Galaxy|Redmi|Mate|P)\s*\d+",
        "Tablet": r"(iPad|Tab|MatePad)",
        "Laptop": r"(MacBook|MateBook|Mi Notebook)"
    }
    for category, pattern in product_patterns.items():
        if re.search(pattern, product_name, re.IGNORECASE):
            return category
    return "Other"

import time  # Add this import at the top of views.py

def scrape_products():
    """Scrape products from GSM Arena's desktop site for Samsung, Apple, Huawei, and Xiaomi."""
    product_info_list = []
    urls = {
        "Samsung": "https://www.gsmarena.com/samsung-phones-9.php",
        "Apple": "https://www.gsmarena.com/apple-phones-48.php",
        "Huawei": "https://www.gsmarena.com/huawei-phones-58.php",
        "Xiaomi": "https://www.gsmarena.com/xiaomi-phones-80.php"
    }
    for brand, url in urls.items():
        time.sleep(1)  # ✅ Wait 3 seconds before each request to prevent rate limiting
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
    """Display products with brand, series, and product type filtering."""
    product_info_list = scrape_products()
    selected_brands = request.GET.getlist('brand')
    selected_series = request.GET.getlist('series')
    selected_types = request.GET.getlist('type')

    print("Selected Brands:", selected_brands)
    print("Selected Series:", selected_series)
    print("Selected Types:", selected_types)
    print("Total Products Before Filtering:", len(product_info_list))

    if selected_brands:
        product_info_list = [p for p in product_info_list if p['brand'] in selected_brands]
    if selected_series:
        product_info_list = [p for p in product_info_list if any(series in p['series'] for series in selected_series)]
    if selected_types:
        product_info_list = [p for p in product_info_list if p['type'] in selected_types]

    print("Filtered Products Count:", len(product_info_list))  # Debugging
    print("Filtered Products:", product_info_list[:5])  # Show first 5 products

    return render(request, 'products.html', {
        'products': product_info_list,
        'selected_brands': selected_brands,
        'selected_series': selected_series,
        'selected_types': selected_types
    })


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


def product_detail(request):
    """Fetch and return product details including AI rating."""
    product_url = request.GET.get("url", None)
    if not product_url:
        return JsonResponse({"error": "Product URL is missing"}, status=400)

    try:
        product_data = scrape_product_details(product_url)
        if not product_data:
            return JsonResponse({"error": "Failed to scrape product details"}, status=500)

        return JsonResponse(product_data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.shortcuts import render
from .models import Product  # ✅ Ensure you have a Product model


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
