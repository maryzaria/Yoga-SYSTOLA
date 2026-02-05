from django.conf import settings
from django.contrib.auth import get_user_model


def ensure_admin_password():
    password = getattr(settings, "DJANGO_ADMIN_PASSWORD", "")
    if not password:
        return

    username = getattr(settings, "DJANGO_ADMIN_USERNAME", "admin")
    email = getattr(settings, "DJANGO_ADMIN_EMAIL", "admin@example.com")

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
    )

    if created:
        user.set_password(password)
        user.save(update_fields=["password"])
        return

    if not user.check_password(password):
        user.set_password(password)
        user.save(update_fields=["password"])
