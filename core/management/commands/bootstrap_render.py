from django.core.management.base import BaseCommand

from core.bootstrap import bootstrap_render


class Command(BaseCommand):
    help = "Bootstrap Render: update Site and SocialApp without shell access"

    def handle(self, *args, **options):
        bootstrap_render()
        self.stdout.write("Bootstrap complete")
