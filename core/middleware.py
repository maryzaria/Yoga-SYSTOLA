from django.core.cache import cache
from django.shortcuts import redirect

from .odoo_allowlist import is_email_allowed


class AllowlistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        path = request.path or ""

        if user and user.is_authenticated:
            if not user.is_active:
                if path.startswith("/pending/") or path.startswith("/accounts/logout/"):
                    return self.get_response(request)
                if path.startswith("/admin/") or path.startswith("/static/"):
                    return self.get_response(request)

                cache_key = f"allowlist:{user.email}"
                cached = cache.get(cache_key)
                if cached is None:
                    cached = is_email_allowed(user.email)
                    cache.set(cache_key, cached, 600)

                if cached:
                    user.is_active = True
                    user.save(update_fields=["is_active"])
                else:
                    return redirect("/pending/")

        return self.get_response(request)
