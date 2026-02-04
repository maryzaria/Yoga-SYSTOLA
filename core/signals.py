from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from .models import Profile
from .odoo import create_lead


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(user_signed_up)
def send_signup_to_odoo(request, user, **kwargs):
    create_lead(
        name="SYSTOLA — New Signup",
        email=user.email,
        description="New user signup",
    )
