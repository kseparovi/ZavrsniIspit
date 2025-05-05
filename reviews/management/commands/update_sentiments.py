from django.core.management.base import BaseCommand
from reviews.models import ProductReview, Product
from textblob import TextBlob
from transformers import pipeline
from tqdm import tqdm

bert_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

class Command(BaseCommand):
    help = "Ažurira sentiment za sve recenzije i ponovno računa prosječnu ocjenu proizvoda."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help="Prisilno ažuriraj sve recenzije")

    def handle(self, *args, **options):
        force = options['force']
        reviews = ProductReview.objects.all()

        self.stdout.write(self.style.SUCCESS(f"🔄 Ažuriranje sentimenta za {reviews.count()} recenzija..."))
        updated_count = 0

        for review in tqdm(reviews):
            if not force and review.sentiment_score is not None:
                continue

            # TextBlob
            polarity = TextBlob(review.comment).sentiment.polarity
            review.textblob_sentiment_score = polarity
            review.sentiment_score = round((polarity + 1) * 5, 2)
            review.rating = round((polarity + 1) * 5)

            # BERT
            try:
                result = bert_analyzer(review.comment[:512])[0]
                review.bert_sentiment_label = result['label']
                review.bert_sentiment_score = round(result['score'], 3)
            except Exception as e:
                self.stderr.write(f"BERT greška: {e}")
                review.bert_sentiment_label = None
                review.bert_sentiment_score = None

            review.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Ažurirano sentiment polje za {updated_count} recenzija."))

        # Ažuriranje ai_rating za sve proizvode
        self.stdout.write("📈 Računam nove AI ocjene za proizvode...")
        for product in Product.objects.all():
            reviews = product.reviews.filter(sentiment_score__isnull=False)
            score = self.calculate_final_score(reviews)
            product.ai_rating = score
            product.save()

        self.stdout.write(self.style.SUCCESS("🎯 Gotovo! AI ocjene ažurirane."))

    def calculate_final_score(self, reviews):
        total = 0
        weight_sum = 0
        for r in reviews:
            score = r.sentiment_score
            strength = abs(score - 5)
            if strength < 1:
                continue  # preskoči neutralne

            length_weight = min(len(r.comment) / 300, 1)
            weight = strength * length_weight
            total += score * weight
            weight_sum += weight

        return round(total / weight_sum, 1) if weight_sum else 5.0
