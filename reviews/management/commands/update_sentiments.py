from django.core.management.base import BaseCommand
from reviews.models import ProductReview, Product
from textblob import TextBlob
from transformers import pipeline
from tqdm import tqdm

# ✅ Koristi stabilniji, laganiji model koji ne zahtijeva tiktoken ni sentencepiece
bert_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)

class Command(BaseCommand):
    help = "Ažurira sentiment za sve recenzije i ponovno računa prosječnu ocjenu proizvoda."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help="Prisilno ažuriraj sve recenzije")

    def handle(self, *args, **options):
        force = options['force']
        reviews = ProductReview.objects.all()

        self.stdout.write(self.style.SUCCESS(f"🔄 Ažuriram sentiment za {reviews.count()} recenzija..."))
        updated_count = 0

        for review in tqdm(reviews):
            if not force and review.sentiment_score is not None:
                continue

            comment = review.comment.strip()
            if len(comment) < 20:
                # Prekratki komentari se tretiraju kao neutralni
                review.sentiment_score = 5.0
                review.rating = 3
                review.bert_sentiment_label = None
                review.bert_sentiment_score = None
                review.textblob_sentiment_score = None
            else:
                # 🔍 TextBlob analiza
                tb_polarity = TextBlob(comment).sentiment.polarity
                tb_score_scaled = (tb_polarity + 1) * 2.5  # skala 0–5
                review.textblob_sentiment_score = round(tb_polarity, 3)

                # 🤖 BERT analiza
                try:
                    bert_result = bert_analyzer(comment[:512])[0]
                    label = bert_result['label']
                    score = bert_result['score']
                    review.bert_sentiment_label = label
                    review.bert_sentiment_score = round(score, 3)

                    if label == "POSITIVE":
                        bert_score_scaled = 5.0
                    elif label == "NEGATIVE":
                        bert_score_scaled = 0.0
                    else:
                        bert_score_scaled = 2.5
                except Exception as e:
                    self.stderr.write(f"BERT greška: {e}")
                    review.bert_sentiment_label = None
                    review.bert_sentiment_score = None
                    bert_score_scaled = 2.5

                # 🧠 Kombinirani (hibridni) score
                final_score = round((0.6 * bert_score_scaled + 0.4 * tb_score_scaled), 2)
                review.sentiment_score = final_score
                review.rating = min(max(round(final_score), 1), 5)

            review.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Ažurirano sentiment polje za {updated_count} recenzija."))

        # 📊 Ažuriraj prosječne ocjene za proizvode
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
                continue  # neutralne ignoriramo

            length_weight = min(len(r.comment) / 300, 1)
            weight = strength * length_weight
            total += score * weight
            weight_sum += weight

        return round(total / weight_sum, 1) if weight_sum else 5.0
