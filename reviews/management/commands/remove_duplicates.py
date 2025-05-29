from django.core.management.base import BaseCommand
from reviews.models import ProductReview
from collections import defaultdict
import re

class Command(BaseCommand):
    help = 'Uklanja duplikate i odgovore na recenzije (citati + datumi)'

    def handle(self, *args, **kwargs):
        seen = defaultdict(list)
        all_reviews = ProductReview.objects.all()
        duplicates_removed = 0
        replies_removed = 0

        # Regex: "Ime, 28 May 2024" ili bilo koji tekst s datumom tog oblika
        date_pattern = re.compile(r"\b\w{2,20},? ?\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}", re.IGNORECASE)

        # Prepoznaj poznate citate korisnika koji se ponavljaju kao odgovori
        known_reply_starts = [
            "let me be ,", "antfranc,", "garbear,", "lol,", "anonymous,",
            "apox,", "razi,", "snelleboi,", "james holden,", "brainless u,"
        ]

        for review in all_reviews:
            comment = review.comment.strip()
            comment_lower = comment.lower()

            # Ako sadrži ime + datum → smatra se odgovorom
            if date_pattern.search(comment):
                review.delete()
                replies_removed += 1
                print(f"⛔ Obrisana replika (datum): {comment[:60]}...")
                continue

            # Ako počinje kao poznati "reply" pattern
            if any(comment_lower.startswith(start) for start in known_reply_starts):
                review.delete()
                replies_removed += 1
                print(f"⛔ Obrisana replika (citirani korisnik): {comment[:60]}...")
                continue

            # Ako je isti komentar već zabilježen — obriši kao duplikat
            key = comment_lower
            if key in seen:
                review.delete()
                duplicates_removed += 1
                print(f"♻️ Duplikat obrisan: {comment[:60]}...")
            else:
                seen[key].append(review)

        print(f"\n✅ Završeno čišćenje.")
        print(f"🗑️ Uklonjeno duplikata: {duplicates_removed}")
        print(f"🗑️ Uklonjeno odgovora na recenzije: {replies_removed}")
