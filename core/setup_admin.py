from django.conf import settings
from django.contrib.auth import get_user_model


def ensure_admin_password():
    password = getattr(settings, "DJANGO_ADMIN_PASSWORD", "")
    if not password:
        return

    User = get_user_model()
    try:
        user = User.objects.get(username="admin")
    except User.DoesNotExist:
        return

    if not user.check_password(password):
        user.set_password(password)
        user.save(update_fields=["password"])
