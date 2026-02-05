from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from .models import TrainingEvent


class BasicPagesTests(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_teachers_page(self):
        response = self.client.get("/teachers/")
        self.assertEqual(response.status_code, 200)

    def test_schedule_page(self):
        response = self.client.get("/schedule/")
        self.assertEqual(response.status_code, 200)


class AuthPagesTests(TestCase):
    def test_login_page(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_signup_page(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_password_reset_page(self):
        response = self.client.get("/accounts/password/reset/")
        self.assertEqual(response.status_code, 200)


class PendingAccessTests(TestCase):
    @override_settings(ODOO_ALLOW_TAG="")
    def test_pending_page_anonymous(self):
        response = self.client.get("/pending/")
        self.assertEqual(response.status_code, 200)

    @override_settings(ODOO_ALLOW_TAG="")
    def test_pending_check_redirects(self):
        response = self.client.post("/pending/check/")
        self.assertEqual(response.status_code, 302)


class ScheduleLogicTests(TestCase):
    def test_event_listed_this_week(self):
        now = timezone.now()
        start = now + timedelta(days=1)
        TrainingEvent.objects.create(
            uid="event-1",
            title="Test",
            start=start,
            status="confirmed",
            is_active=True,
        )
        response = self.client.get("/schedule/")
        self.assertEqual(response.status_code, 200)
