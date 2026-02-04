from django.contrib import admin

from .models import JoinClick, Profile, TrainingEvent


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "trainings_completed")


@admin.register(TrainingEvent)
class TrainingEventAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end", "status", "is_active")
    list_filter = ("status", "is_active")
    search_fields = ("title", "description", "location", "uid")


@admin.register(JoinClick)
class JoinClickAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "clicked_at", "ip_address")
    list_filter = ("clicked_at",)
