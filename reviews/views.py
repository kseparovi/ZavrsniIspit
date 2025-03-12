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


def scrape_product_details(url):
    """Scrape product details, rating, and user comments from GSMArena."""
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # ✅ Extract Phone Name
    title_tag = soup.find('h1', class_='specs-phone-name-title')
    product_name = title_tag.text.strip() if title_tag else "Unknown"

    # ✅ Extract Brand from Breadcrumbs
    breadcrumb = soup.find('div', class_='breadcrumb')
    brand = breadcrumb.find_all('a')[1].text.strip() if breadcrumb and len(breadcrumb.find_all('a')) > 1 else "Unknown"

    # ✅ Extract Series (Infer from Name)
    series = "Undefined"
    if "Galaxy A" in product_name:
        series = "Galaxy A"
    elif "Galaxy S" in product_name:
        series = "Galaxy S"
    elif "iPhone" in product_name:
        series = "iPhone"
    elif "Redmi" in product_name:
        series = "Redmi"
    elif "Pixel" in product_name:
        series = "Google Pixel"

    # ✅ Extract Type (Based on Known Categories)
    if "Fold" in product_name or "Flip" in product_name:
        phone_type = "Foldable"
    elif "Gaming" in product_name:
        phone_type = "Gaming Phone"
    else:
        phone_type = "Smartphone"

    # ✅ Extract Rating (Popularity %)
    rating_tag = soup.find('strong', class_='accent')
    rating = rating_tag.text.strip() if rating_tag else "No rating"

    # ✅ Extract Key Specs
    specs_list = []
    specs_div = soup.find('ul', class_='specs-spotlight-features')
    if specs_div:
        specs_items = specs_div.find_all('span', {'data-spec': True})
        for item in specs_items:
            specs_list.append(item.text.strip())

    specs_text = ", ".join(specs_list) if specs_list else "No specs found"

    # ✅ Extract User Comments
    comments = []
    comments_section = soup.find('div', id='user-comments')

    if comments_section:
        comment_threads = comments_section.find_all('div', class_='user-thread')
        for thread in comment_threads:  # ✅ Capture all available comments
            user = thread.find('li', class_='uname')
            username = user.text.strip() if user else "Anonymous"

            comment = thread.find('p', class_='uopin')
            comment_text = comment.text.strip() if comment else "No comment"

            comments.append({"username": username, "comment": comment_text})

    # ✅ Get More Comments from "Read all opinions" Page
    more_comments_link = comments_section.find('a', href=True, text="Read all opinions") if comments_section else None
    if more_comments_link:
        full_comments_url = f"https://www.gsmarena.com/{more_comments_link['href']}"
        try:
            more_comments_response = requests.get(full_comments_url, headers=headers)
            if more_comments_response.status_code == 200:
                more_soup = BeautifulSoup(more_comments_response.text, 'html.parser')
                extra_comment_threads = more_soup.find_all('div', class_='user-thread')

                for thread in extra_comment_threads[:10]:  # ✅ Get 10 additional comments
                    user = thread.find('li', class_='uname')
                    username = user.text.strip() if user else "Anonymous"

                    comment = thread.find('p', class_='uopin')
                    comment_text = comment.text.strip() if comment else "No comment"

                    comments.append({"username": username, "comment": comment_text})
        except Exception as e:
            print(f"Error fetching additional comments: {e}")

    # Debugging output to verify extraction
    print(f"Scraped Data for {url}:")
    print(f"Product Name: {product_name}")
    print(f"Brand: {brand}")
    print(f"Series: {series}")
    print(f"Type: {phone_type}")
    print(f"Rating: {rating}")
    print(f"Specs: {specs_text}")
    print(f"Total Comments: {len(comments)}")

    return {
        "name": product_name,
        "brand": brand,
        "series": series,
        "type": phone_type,
        "rating": rating,
        "specs": specs_text,
        "comments": comments
    }


def product_detail(request):
    """Django view to fetch product details dynamically."""
    product_url = request.GET.get('url')
    if not product_url:
        return JsonResponse({"error": "No URL provided"}, status=400)

    product_data = scrape_product_details(product_url)
    if not product_data:
        return JsonResponse({"error": "Failed to fetch product details"}, status=500)

    return JsonResponse(product_data)


from django.shortcuts import render
from .models import Product  # ✅ Ensure you have a Product model


def search_results(request):
    query = request.GET.get("query", "")

    # Filter products based on search query (assuming you have a `name` field in the model)
    products = Product.objects.filter(name__icontains=query) if query else []

    return render(request, "search_results.html", {"query": query, "products": products})
