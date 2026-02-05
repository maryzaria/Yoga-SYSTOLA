from django.core.cache import cache
from django.shortcuts import redirect

from .odoo_allowlist import is_email_allowed
from .user_utils import get_user_email


class AllowlistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        path = request.path or ""

        if user and user.is_authenticated and not user.is_staff:
            if path.startswith("/pending/") or path.startswith("/accounts/logout/"):
                return self.get_response(request)
            if path.startswith("/admin/") or path.startswith("/static/"):
                return self.get_response(request)

            email = get_user_email(user)
            if email and user.email != email:
                user.email = email
                user.save(update_fields=["email"])

            if not email:
                return redirect("/pending/")

            cache_key = f"allowlist:{email}"
            cached = cache.get(cache_key)
            if cached is None:
                cached = is_email_allowed(email)
                cache.set(cache_key, cached, 600)

            if not cached:
                return redirect("/pending/")

        return self.get_response(request)
