
from django.core.management.base import BaseCommand
from django.utils import timezone
from reviews.models import Product, Review


def scrape_gsmarena_products(url):
    # Placeholder for the actual scraping logic
    # This function should return a list of dictionaries with product details
    return [
        {
            "name": "Sample Product",
            "brand": "Sample Brand",
            "series": "Sample Series",
            "type": "Sample Type",
            "image_url": "http://example.com/image.jpg",
            "product_link": url,
            "phonearena_link": url,
            "dimensions": "Sample Dimensions",
            "os": "Sample OS",
            "display_size": "Sample Display Size",
            "chipset": "Sample Chipset",
            "battery": "Sample Battery",
            "memory": "Sample Memory",
            "camera": "Sample Camera"
        }
    ]

class Command(BaseCommand):

    help = "Scrape GSM Arena products and save to the database."

    def handle(self, *args, **kwargs):
        url = "http://example.com"  # Replace with the actual URL
        self.stdout.write(f"🔍 Starting product scrape from {url}...\n")

        products_data = scrape_gsmarena_products(url)
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults={
                    "brand": product_data["brand"],
                    "series": product_data["series"],
                    "type": product_data["type"],
                    "image_url": product_data["image_url"],
                    "product_link": product_data["product_link"],
                    "phonearena_link": product_data["phonearena_link"],
                    "dimensions": product_data["dimensions"],
                    "os": product_data["os"],
                    "display_size": product_data["display_size"],
                    "chipset": product_data["chipset"],
                    "battery": product_data["battery"],
                    "memory": product_data["memory"],
                    "camera": product_data["camera"]
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created new product: {product.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Product already exists: {product.name}"))