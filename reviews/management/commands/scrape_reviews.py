import requests
import random
import time
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from reviews.models import Product, Review
from reviews.views import scrape_gsmarena_reviews

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
def scrape_gsmarena_specs(product):
    print(f"Scraping specifications for {product.name}...")
    url = product.product_link

    try:
        headers = get_random_headers()
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch specs page, status: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        specs = {
            'display_size': None,
            'battery': None,
            'chipset': None,
            'memory': None,
            'camera': None
        }

        # SPEC SCRAPING
        spec_table = soup.find('div', id='specs-list')
        if spec_table:
            rows = spec_table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.text.strip().lower()
                    value = td.text.strip()

                    if 'display' in key or 'size' in key:
                        specs['display_size'] = value
                    if 'battery' in key:
                        specs['battery'] = value
                    if 'chipset' in key:
                        specs['chipset'] = value
                    if 'internal' in key or 'memory' in key:
                        specs['memory'] = value
                    if 'camera' in key:
                        specs['camera'] = value

        # Update product
        Product.objects.filter(id=product.id).update(
            display_size=specs['display_size'],
            battery=specs['battery'],
            chipset=specs['chipset'],
            memory=specs['memory'],
            camera=specs['camera']
        )
        print(f"Updated specs for {product.name}")

    except Exception as e:
        print(f"Error scraping specs for {product.name}: {str(e)}")


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
    help = "Scrape reviews and specifications"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        print(f"Scraping data for {len(products)} products...")

        for product in products:
            # ✅ Scrape Specs
            scrape_gsmarena_specs(product)

            # ✅ Scrape Reviews (Correct argument passing!)
            if product.product_link:
                scrape_gsmarena_reviews(product.product_link, product)
            if product.phonearena_link:
                scrape_phonearena_reviews(product.phonearena_link, product)

            # Optional: Sleep to avoid rate limits
            time.sleep(random.uniform(2, 4))

        print("All scraping completed.")
