import requests
import random
import time
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from reviews.models import Product, Review

# List of User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/87.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/87.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/89.0.774.68",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/89.0.774.68",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
    # Add more as needed
]

# Helper function to get random headers
def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

# GSM Arena scraper
def scrape_gsmarena_reviews(product):
    print(f"Scraping GSM Arena reviews for {product.name}...")
    url = product.product_link

    try:
        headers = get_random_headers()
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            print("Too many requests (429), sleeping...")
            time.sleep(random.uniform(5, 10))
            headers = get_random_headers()
            response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch GSM Arena page, status: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # Parse reviews - adjust according to actual page structure
        review_elements = soup.select("div.user-thread")
        count = 0
        for element in review_elements:
            username = element.select_one(".uname").get_text(strip=True)
            review_text = element.select_one(".uopin").get_text(strip=True)

            existing_review = Review.objects.filter(product=product, comment=review_text).first()
            if not existing_review:
                Review.objects.create(product=product, username=username, comment=review_text)
                count += 1

        print(f"Scraped {count} GSM reviews for {product.name}")

    except Exception as e:
        print(f"Error scraping GSM Arena for {product.name}: {str(e)}")

# Phone Arena scraper (stub example)
def scrape_phonearena_reviews(product):
    print(f"Scraping PhoneArena reviews for {product.name}...")
    # Example URL structure - adjust this accordingly
    base_url = f"https://www.phonearena.com/phones/{product.name.replace(' ', '-')}/reviews"

    try:
        headers = get_random_headers()
        response = requests.get(base_url, headers=headers)

        if response.status_code == 429:
            print("Too many requests (429), sleeping...")
            time.sleep(random.uniform(5, 10))
            headers = get_random_headers()
            response = requests.get(base_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch PhoneArena page, status: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        review_elements = soup.select("div.user-review")
        count = 0
        for element in review_elements:
            username = element.select_one(".reviewer-name").get_text(strip=True)
            review_text = element.select_one(".review-body").get_text(strip=True)

            existing_review = Review.objects.filter(product=product, comment=review_text).first()
            if not existing_review:
                Review.objects.create(product=product, username=username, comment=review_text)
                count += 1

        print(f"Scraped {count} PhoneArena reviews for {product.name}")

    except Exception as e:
        print(f"Error scraping PhoneArena for {product.name}: {str(e)}")

# Django command class
class Command(BaseCommand):
    help = "Scrape reviews from GSM Arena and Phone Arena"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        print(f"Scraping reviews for {len(products)} products...")

        for product in products:
            scrape_gsmarena_reviews(product)
            scrape_phonearena_reviews(product)
            time.sleep(random.uniform(2, 5))  # Delay between products to avoid rate limits
