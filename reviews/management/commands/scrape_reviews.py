import time
import requests
import re
import random
from bs4 import BeautifulSoup
from textblob import TextBlob
from django.core.management.base import BaseCommand
from reviews.models import Product, Review


def get_random_headers():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(USER_AGENTS)}


def scrape_gsmarena_reviews(product_url, product_obj):
    print(f"Scraping reviews from GSM Arena: {product_url}")
    response = requests.get(product_url, headers=get_random_headers())

    if response.status_code != 200:
        return
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


def scrape_phonearena_reviews(phonearena_url, product_obj):
    print(f"Scraping PhoneArena reviews from: {phonearena_url}")
    response = requests.get(phonearena_url, headers=get_random_headers())

    if response.status_code != 200:
        print(f"❌ PhoneArena page failed: {response.status_code}")
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    comment_blocks = soup.find_all("div", class_="components-MessageLayout-index__message-view")
    for block in comment_blocks:
        username_tag = block.find("span", {"data-spot-im-class": "message-username"})
        comment_tag = block.find("div", {"data-spot-im-class": "message-text"})
        username = username_tag.get_text(strip=True) if username_tag else "Anonymous"
        comment = comment_tag.get_text(strip=True) if comment_tag else ""
        if comment and not Review.objects.filter(product=product_obj, username=username, comment=comment).exists():
            Review.objects.create(product=product_obj, username=username, comment=comment)
            print(f"✅ PhoneArena comment by {username}: {comment[:60]}...")


def scrape_additional_specs(product_url, product_obj):
    headers = get_random_headers()
    response = requests.get(product_url, headers=headers)

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

    print(f"✅ Updated GSM Arena specs for {product_obj.name}")


def scrape_phonearena_specs(phonearena_url, product_obj):
    print(f"🔍 Scraping PhoneArena specs from: {phonearena_url}")
    headers = get_random_headers()
    response = requests.get(phonearena_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to load PhoneArena page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    specs = {
        'display_size': None,
        'battery': None,
        'chipset': None,
        'memory': None,
        'camera': None,
    }

    spec_sections = soup.find_all('div', class_='s_specs_box')
    for section in spec_sections:
        title_div = section.find('div', class_='s_specs_title')
        if not title_div:
            continue
        title = title_div.text.strip().lower()

        rows = section.find_all('li')
        for row in rows:
            label = row.find('span', class_='s_specs_label')
            value = row.find('span', class_='s_specs_value')

            if not label or not value:
                continue

            label_text = label.text.strip().lower()
            value_text = value.text.strip()

            if 'display' in title and not specs['display_size']:
                specs['display_size'] = value_text
            elif 'battery' in title and not specs['battery']:
                specs['battery'] = value_text
            elif 'hardware' in title:
                if 'chipset' in label_text:
                    specs['chipset'] = value_text
                elif 'ram' in label_text or 'storage' in label_text:
                    specs['memory'] = value_text
            elif 'camera' in title and not specs['camera']:
                specs['camera'] = value_text

    Product.objects.filter(id=product_obj.id).update(
        display_size=specs['display_size'],
        battery=specs['battery'],
        chipset=specs['chipset'],
        memory=specs['memory'],
        camera=specs['camera'],
    )

    print(f"✅ Updated PhoneArena specs for {product_obj.name}")


# Enhanced Amazon scraper with fallback and logging
def scrape_amazon_reviews(product_url, product_obj):
    print(f"Scraping Amazon reviews from: {product_url}")

    headers = get_random_headers()

    try:
        response = requests.get(product_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Amazon page failed: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = soup.find_all("li", {"data-hook": "review"})

        if not reviews:
            print(f"⚠️ No reviews found on Amazon page: {product_url}")
            return

        for review in reviews:
            try:
                username_tag = review.find("span", class_="a-profile-name")
                rating_tag = review.find("i", {"data-hook": "review-star-rating"})
                title_tag = review.find("a", {"data-hook": "review-title"})
                body_tag = review.find("span", {"data-hook": "review-body"})
                date_tag = review.find("span", {"data-hook": "review-date"})

                if not all([username_tag, rating_tag, title_tag, body_tag]):
                    continue

                username = username_tag.get_text(strip=True)
                rating_text = rating_tag.find("span").text
                rating = float(rating_text.split(" ")[0])
                title = title_tag.find("span").text.strip()
                body = body_tag.get_text(strip=True)
                date = date_tag.get_text(strip=True) if date_tag else ""

                if Review.objects.filter(product=product_obj, username=username, comment=body).exists():
                    continue

                Review.objects.create(
                    product=product_obj,
                    username=username,
                    title=title,
                    comment=body,
                    source_url=product_url
                )

                print(f"✅ Amazon review by {username}: {title[:30]}...")

            except Exception as parse_error:
                print(f"⚠️ Parsing error on one review: {parse_error}")

    except Exception as fetch_error:
        print(f"❌ Failed to fetch Amazon page: {fetch_error}")


from reviews.utils import sync_reviews_to_product_reviews

class Command(BaseCommand):
    help = "Scrape reviews and specs from GSM Arena, PhoneArena, and Amazon for all products."

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        self.stdout.write(f"🔍 Starting review scrape for {products.count()} products...\n")

        for product in products:
            if not product.product_link:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipping {product.name}: No GSM Arena link"))
                continue

            self.stdout.write(f"📱 Scraping reviews for {product.name}...")

            try:
                scrape_gsmarena_reviews(product.product_link, product)

                if product.phonearena_link:
                    scrape_phonearena_reviews(product.phonearena_link, product)
                else:
                    self.stdout.write(f"⚠️ No PhoneArena link for {product.name}, skipping PhoneArena scraping.")

                if hasattr(product, 'amazon_link') and product.amazon_link:
                    scrape_amazon_reviews(product.amazon_link, product)
                else:
                    self.stdout.write(f"⚠️ No Amazon link for {product.name}, skipping Amazon scraping.")

                if not product.display_size or not product.battery or not product.chipset:
                    if product.product_link:
                        scrape_additional_specs(product.product_link, product)
                        product.refresh_from_db()
                    if product.phonearena_link:
                        scrape_phonearena_specs(product.phonearena_link, product)
                        product.refresh_from_db()

                self.stdout.write(self.style.SUCCESS(f"✅ Done with {product.name}\n"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error while scraping {product.name}: {e}"))

        self.stdout.write("🔄 Syncing into ProductReview...")
        sync_reviews_to_product_reviews()
        self.stdout.write(self.style.SUCCESS("✅ All products scraped successfully!"))
