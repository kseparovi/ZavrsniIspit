from django.core.management.base import BaseCommand
from reviews.models import Product
from reviews.views import analyze_sentiment_and_update_rating

class Command(BaseCommand):
    help = "Analyze reviews and update average ratings"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            analyze_sentiment_and_update_rating(product)
        self.stdout.write(self.style.SUCCESS("All product ratings updated!"))
