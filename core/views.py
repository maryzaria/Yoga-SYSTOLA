from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
import re

from django.utils import timezone
from django.utils.html import strip_tags
from zoneinfo import ZoneInfo
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour

from .models import JoinClick, TrainingEvent
from .odoo import create_lead
from .teachers_data import TEACHERS
from .odoo_allowlist import allowlist_debug, is_email_allowed
from .user_utils import get_user_email
from django.core.cache import cache


def home(request):
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    if not request.user.is_active:
        return redirect("/pending/")
    profile = request.user.profile
    return render(request, "core/dashboard.html", {"profile": profile})


def pending(request):
    allowed = None
    debug_info = None
    if request.user.is_authenticated:
        email = get_user_email(request.user)
        if email and request.user.email != email:
            request.user.email = email
            request.user.save(update_fields=["email"])
        if email:
            allowed = is_email_allowed(email)
            debug_info = allowlist_debug(email)
    return render(
        request,
        "core/pending.html",
        {"allowed": allowed, "debug_info": debug_info},
    )


def pending_check(request):
    if request.method != "POST":
        return redirect("/pending/")

    if not request.user.is_authenticated:
        return redirect("/pending/")

    email = get_user_email(request.user)
    if not email:
        return redirect("/pending/")
    if request.user.email != email:
        request.user.email = email
        request.user.save(update_fields=["email"])
    allowed = is_email_allowed(email)
    cache.set(f"allowlist:{email}", allowed, 600)
    if allowed:
        request.user.is_active = True
        request.user.save(update_fields=["is_active"])
    return redirect("/pending/")


def schedule(request):
    now = timezone.localtime()
    week_start = (now - timezone.timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_end = week_start + timezone.timedelta(days=7)
    upcoming_events = TrainingEvent.objects.filter(
        status="confirmed", start__gte=now, start__lt=week_end
    ).order_by("start")
    next_event = upcoming_events[0] if upcoming_events else None
    time_zones = [
        ("NY", "America/New_York"),
        ("DE", "Europe/Berlin"),
        ("KV", "Europe/Kyiv"),
        ("MSQ", "Europe/Minsk"),
        ("GE", "Asia/Tbilisi"),
        ("KZ", "Asia/Almaty"),
        ("BKK", "Asia/Bangkok"),
    ]
    next_event_times = []
    if next_event:
        for label, tz_name in time_zones:
            local_time = next_event.start.astimezone(ZoneInfo(tz_name))
            next_event_times.append((label, local_time))
    next_event_times_list = []
    if next_event_times:
        next_event_times_list = [
            f"{t.strftime('%H:%M')} {label}" for label, t in next_event_times
        ]
    next_event_times_str = strip_tags(" / ".join(next_event_times_list))

    url_pattern = re.compile(r"(https?://\S+|www\.\S+)")
    events_display = []
    for event in upcoming_events:
        duration_minutes = None
        if event.end:
            delta = event.end - event.start
            minutes = int(delta.total_seconds() // 60)
            if minutes > 0:
                duration_minutes = minutes
        description = strip_tags(event.description)
        description = url_pattern.sub("", description).strip()
        events_display.append(
            {
                "event": event,
                "duration_minutes": duration_minutes,
                "description": description,
            }
        )
    return render(
        request,
        "core/schedule.html",
        {
            "events": events_display,
            "next_event": next_event,
            "next_event_times": next_event_times,
            "next_event_times_list": next_event_times_list,
            "next_event_times_str": next_event_times_str,
            "zoom_join_url": settings.ZOOM_JOIN_URL,
        },
    )


def teachers(request):
    return render(request, "core/teachers.html", {"teachers": TEACHERS})


@login_required
def join_click(request):
    if request.method != "POST":
        return HttpResponseForbidden("Only POST allowed")

    event_id = request.POST.get("event_id")
    event = None
    if event_id:
        event = TrainingEvent.objects.filter(id=event_id).first()

    JoinClick.objects.create(
        user=request.user,
        event=event,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )
    try:
        description = "Join click"
        if event:
            description = f"Join click: {event.title or 'Training'} at {event.start}"
        create_lead(
            name="SYSTOLA — Join Click",
            email=request.user.email,
            description=description,
        )
    except Exception:
        pass
    return redirect(settings.ZOOM_JOIN_URL)


@login_required
def refresh_schedule(request):
    if request.method != "POST":
        return HttpResponseForbidden("Only POST allowed")

    from django.core.management import call_command

    call_command("sync_calendar")
    return redirect("/schedule/")


@user_passes_test(lambda u: u.is_staff)
def analytics(request):
    total_clicks = JoinClick.objects.count()
    unique_users = JoinClick.objects.values("user_id").distinct().count()
    clicks_by_event = (
        JoinClick.objects.values("event__title")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    trainings_total = (
        get_user_model()
        .objects.filter(profile__isnull=False)
        .aggregate(total=Sum("profile__trainings_completed"))["total"]
        or 0
    )
    recent_clicks = JoinClick.objects.select_related("user", "event")[:20]
    clicks_by_hour_raw = (
        JoinClick.objects.annotate(hour=ExtractHour("clicked_at"))
        .values("hour")
        .annotate(total=Count("id"))
    )
    hour_map = {item["hour"]: item["total"] for item in clicks_by_hour_raw}
    clicks_by_hour = [{"hour": h, "total": hour_map.get(h, 0)} for h in range(24)]

    clicks_by_user = (
        JoinClick.objects.values("user__email")
        .annotate(total=Count("id"))
        .order_by("-total")[:20]
    )

    return render(
        request,
        "core/analytics.html",
        {
            "total_clicks": total_clicks,
            "unique_users": unique_users,
            "clicks_by_event": clicks_by_event,
            "trainings_total": trainings_total,
            "recent_clicks": recent_clicks,
            "clicks_by_hour": clicks_by_hour,
            "clicks_by_user": clicks_by_user,
        },
    )
