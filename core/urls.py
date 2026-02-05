from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("schedule/", views.schedule, name="schedule"),
    path("join/", views.join_click, name="join_click"),
    path("schedule/refresh/", views.refresh_schedule, name="refresh_schedule"),
    path("analytics/", views.analytics, name="analytics"),
    path("teachers/", views.teachers, name="teachers"),
    path("pending/", views.pending, name="pending"),
    path("pending/check/", views.pending_check, name="pending_check"),
    path("odoo-contacts/", views.odoo_contacts, name="odoo_contacts"),
]
