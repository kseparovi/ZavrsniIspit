from django.contrib.auth import authenticate
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from bs4 import BeautifulSoup
import re

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
        html_content = get_content(url)
        if not html_content:
            continue
        soup = BeautifulSoup(html_content, 'html.parser')
        product_list_div = soup.find('div', class_='makers')
        if not product_list_div:
            print(f"Error: Could not find product list for {brand}")
            print(f"Fetched HTML Preview: {soup.prettify()[:500]}")
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
