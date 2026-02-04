from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    trainings_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile({self.user.email})"


class TrainingEvent(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    uid = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="confirmed")
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=64, default="google_calendar")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return f"{self.title} ({self.start})"


class JoinClick(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="join_clicks"
    )
    event = models.ForeignKey(
        TrainingEvent, on_delete=models.SET_NULL, null=True, blank=True
    )
    clicked_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-clicked_at"]

    def __str__(self):
        return f"JoinClick({self.user_id} at {self.clicked_at})"
