from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site


def bootstrap_render():
    domain = settings.SITE_DOMAIN
    site, _ = Site.objects.get_or_create(id=1)
    site.domain = domain
    site.name = domain
    site.save()

    client_id = settings.GOOGLE_CLIENT_ID
    secret = settings.GOOGLE_CLIENT_SECRET
    if not client_id or not secret:
        return

    app, _ = SocialApp.objects.get_or_create(
        provider="google", defaults={"name": "Google"}
    )
    app.name = "Google"
    app.client_id = client_id
    app.secret = secret
    app.key = ""
    app.save()
    app.sites.add(site)
