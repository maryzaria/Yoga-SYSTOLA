from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.odoo_allowlist import is_email_allowed


class Command(BaseCommand):
    help = "Reactivate users whose emails are allowed in Odoo"

    def handle(self, *args, **options):
        User = get_user_model()
        updated = 0
        for user in User.objects.exclude(email=""):
            if is_email_allowed(user.email):
                if not user.is_active:
                    user.is_active = True
                    user.save(update_fields=["is_active"])
                    updated += 1
        self.stdout.write(f"Reactivated users: {updated}")
