from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update admin user from environment variables"

    def handle(self, *args, **options):
        username = getattr(settings, "DJANGO_ADMIN_USERNAME", "admin")
        email = getattr(settings, "DJANGO_ADMIN_EMAIL", "admin@example.com")
        password = getattr(settings, "DJANGO_ADMIN_PASSWORD", "")
        if not password:
            self.stdout.write("DJANGO_ADMIN_PASSWORD is not set, skipping admin setup")
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(f"Admin user created: {username}")
            return

        updated = False
        if user.email != email:
            user.email = email
            updated = True
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            updated = True
        if not user.check_password(password):
            user.set_password(password)
            updated = True
        if updated:
            user.save()
            self.stdout.write(f"Admin user updated: {username}")
