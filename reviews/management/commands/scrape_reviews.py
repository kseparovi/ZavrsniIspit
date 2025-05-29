import requests
import re
import random

from django.core.management import call_command

from reviews.utils import sync_reviews_to_product_reviews
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from reviews.models import Review
import time


def get_random_headers():
    USER_AGENTS = [
        # Add more realistic modern user agents if you want
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        "Mozilla/5.0 (X11; Linux x86_64)..."
    ]
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }



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
    print(f"📅 Scraping PhoneArena reviews from: {phonearena_url}")

    base_url = phonearena_url.rstrip('/') + "/reviews"
    page = 1

    while True:
        url = base_url if page == 1 else f"{base_url}/page/{page}"
        print(f"🔄 Fetching: {url}")
        response = requests.get(url, headers=get_random_headers())
        if response.status_code != 200:
            print(f"❌ Failed to fetch reviews page {page}: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        review_blocks = soup.find_all("h2")  # Headings for each review title
        if not review_blocks:
            print("⚠️ No more reviews found on this page.")
            break

        for title_tag in review_blocks:
            try:
                container = title_tag.find_parent('div')
                title = title_tag.get_text(strip=True)

                user_link = container.find('a', href=lambda x: x and '/user/' in x)
                username = user_link.get_text(strip=True) if user_link else "Anonymous"

                rating = None
                rating_text = title_tag.find_previous(string=True)
                if rating_text and rating_text.strip().isdigit():
                    rating = int(rating_text.strip())

                meta_div = container.find(string=lambda s: s and 'Posted:' in s)
                date_posted = None
                if meta_div:
                    date_posted = meta_div.strip().replace("Posted:", "").strip()

                review_paragraphs = container.find_all('p')
                review_text = " ".join(p.get_text(strip=True) for p in review_paragraphs)

                pros = []
                cons = []

                pros_heading = container.find(string="What I like")
                if pros_heading:
                    pros_ul = pros_heading.find_next('ul')
                    if pros_ul:
                        pros = [li.get_text(strip=True) for li in pros_ul.find_all('li')]

                cons_heading = container.find(string="What I don't like")
                if cons_heading:
                    cons_ul = cons_heading.find_next('ul')
                    if cons_ul:
                        cons = [li.get_text(strip=True) for li in cons_ul.find_all('li')]

                recommendation_text = container.find(string=lambda s: s and 'recommend' in s)
                recommended = None
                if recommendation_text:
                    recommended = "doesn't" not in recommendation_text

                if Review.objects.filter(product=product_obj, username=username, comment=review_text).exists():
                    continue

                Review.objects.create(
                    product=product_obj,
                    username=username,
                    title=title,
                    comment=review_text,
                    rating=rating,
                    source_url=url
                )

                print(f"✅ Saved review by {username}: {title[:40]}...")

            except Exception as e:
                print(f"⚠️ Error parsing a review: {e}")

        page += 1
        time.sleep(2)  # Be polite to PhoneArena's servers





from django.core.management.base import BaseCommand
from reviews.models import Product


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





                self.stdout.write(self.style.SUCCESS(f"✅ Done with {product.name}\n"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error while scraping {product.name}: {e}"))

        self.stdout.write("🔄 Syncing into ProductReview...")
        sync_reviews_to_product_reviews()
        self.stdout.write(self.style.SUCCESS("✅ All products scraped successfully!"))
        self.stdout.write("🧠 Pokrećem analizu sentimenta za sve recenzije...")
        call_command('update_sentiment', '--force')
