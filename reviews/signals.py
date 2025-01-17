# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Signal to make a user admin automatically after creation
@receiver(post_save, sender=User)
def make_user_admin(sender, instance, created, **kwargs):
    if created:
        instance.is_staff = True  # Automatically assign admin privileges
        instance.save()
