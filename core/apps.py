import os

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from . import signals  # noqa: F401

        if os.environ.get("RUN_MAIN") != "true":
            return

        from .setup_admin import ensure_admin_password
        from .scheduler import start_scheduler

        ensure_admin_password()
        start_scheduler()
