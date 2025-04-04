import time
import requests
import re
import random
from bs4 import BeautifulSoup
from textblob import TextBlob
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.core.management.base import BaseCommand
from reviews.models import Product, Review
from reviews.views import scrape_gsmarena_reviews

# ========== Utilities ==========

def get_random_headers():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(USER_AGENTS)}

# ========== User Authentication ==========

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("reviews:home")

def user_signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            auth_login(request, user)
            return redirect("reviews:home")
        else:
            return render(request, "signup.html", {"form": form, "error": "Please correct the errors below"})
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

# ========== Product Logic ==========

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

def scrape_products():
    product_info_list = []
    urls = {
        "Samsung": "https://www.gsmarena.com/samsung-phones-9.php",
        "Apple": "https://www.gsmarena.com/apple-phones-48.php",
        "Huawei": "https://www.gsmarena.com/huawei-phones-58.php",
        "Xiaomi": "https://www.gsmarena.com/xiaomi-phones-80.php"
    }
    for brand, url in urls.items():
        html_content = get_content(url)
        if not html_content:
            continue
        soup = BeautifulSoup(html_content, 'html.parser')
        product_list_div = soup.find('div', class_='makers')
        if not product_list_div:
            continue
        for item in product_list_div.find_all('li'):
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
    products = Product.objects.all().order_by('name')
    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    if selected_series:
        products = products.filter(series__in=selected_series)
    if selected_types:
        products = products.filter(type__in=selected_types)
    return render(request, 'products.html', {
        'products': products,
        'brands': Product.objects.values_list('brand', flat=True).distinct(),
        'series': Product.objects.values_list('series', flat=True).distinct(),
        'types': Product.objects.values_list('type', flat=True).distinct(),
        'selected_brands': selected_brands,
        'selected_series': selected_series,
        'selected_types': selected_types,
    })

def index(request):
    return render(request, 'home.html')

def scrape_gsmarena_reviews(product_url, product_obj):
    print(f"Scraping reviews from: {product_url}")
    response = requests.get(product_url, headers=get_random_headers())
    time.sleep(random.uniform(2, 5))
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    comments_section = soup.find('div', id='user-comments')
    threads = comments_section.find_all('div', class_='user-thread') if comments_section else []
    for thread in threads:
        username_tag = thread.find('li', class_='uname2') or thread.find('li', class_='uname')
        comment_tag = thread.find('p', class_='uopin')
        username = username_tag.text.strip() if username_tag else "Anonymous"
        comment = comment_tag.text.strip() if comment_tag else "No comment"
        if not Review.objects.filter(product=product_obj, username=username, comment=comment).exists():
            Review.objects.create(product=product_obj, username=username, comment=comment)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    return render(request, 'product_detail.html', {'product': product, 'reviews': reviews})

def product_detail_ajax(request):
    product_url = request.GET.get('url')
    product = Product.objects.filter(product_link=product_url).first()
    if not product:
        return JsonResponse({'error': 'Product not found!'}, status=404)
    reviews = Review.objects.filter(product=product)
    comments = [{'username': r.username, 'comment': r.comment} for r in reviews]
    return JsonResponse({
        'name': product.name,
        'brand': product.brand,
        'series': product.series,
        'type': product.type,
        'rating': 'N/A',
        'specs': 'Specs info if you want to add',
        'ai_rating': '4.5',
        'comments': comments
    })

@require_GET
def autocomplete(request):
    query = request.GET.get('query', '').strip()
    matching_products = Product.objects.filter(name__icontains=query).values_list('name', flat=True)
    return JsonResponse(list(matching_products), safe=False)


from django.core.management.base import BaseCommand
from reviews.models import Product
from reviews.views import scrape_gsmarena_reviews

class Command(BaseCommand):
    help = "Scrape GSM Arena reviews for all products."

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        self.stdout.write(f"🔍 Starting review scrape for {products.count()} products...\n")

        for product in products:
            if not product.product_link:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipping {product.name}: No product link"))
                continue

            self.stdout.write(f"📱 Scraping GSM Arena reviews for {product.name}...")

            try:
                scrape_gsmarena_reviews(product.product_link, product)
                self.stdout.write(self.style.SUCCESS(f"✅ Done with {product.name}\n"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed for {product.name}: {e}\n"))

        self.stdout.write(self.style.SUCCESS("✅ All products processed."))
