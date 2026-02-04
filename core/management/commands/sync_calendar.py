from datetime import datetime, time, timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil import rrule
from icalendar import Calendar

from core.models import TrainingEvent


def _normalize_dt(value):
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.combine(value, time.min)

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_default_timezone())
    return dt


class Command(BaseCommand):
    help = "Sync training schedule from Google Calendar iCal feed"

    def handle(self, *args, **options):
        now = timezone.now()
        window_start = now - timedelta(days=1)
        window_end = now + timedelta(days=180)
        url = settings.CALENDAR_ICAL_URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        calendar = Calendar.from_ical(response.text)
        uids_in_feed = set()

        for component in calendar.walk("VEVENT"):
            uid = str(component.get("uid", "")).strip()
            if not uid:
                continue

            summary = str(component.get("summary", "")).strip()
            description = str(component.get("description", "")).strip()
            location = str(component.get("location", "")).strip()
            status = str(component.get("status", "CONFIRMED")).lower()
            status_value = "cancelled" if status == "cancelled" else "confirmed"

            dtstart = component.get("dtstart").dt if component.get("dtstart") else None
            dtend = component.get("dtend").dt if component.get("dtend") else None
            if not dtstart:
                continue

            start = _normalize_dt(dtstart)
            end = _normalize_dt(dtend) if dtend else None
            duration = end - start if end else None

            rrule_prop = component.get("rrule")
            rdate_prop = component.get("rdate")
            exdate_prop = component.get("exdate")

            occurrences = set()
            if rrule_prop:
                rrule_str = rrule_prop.to_ical().decode()
                rule = rrule.rrulestr(rrule_str, dtstart=start)
                occurrences.update(rule.between(window_start, window_end, inc=True))

            if rdate_prop:
                rdates = []
                if hasattr(rdate_prop, "dts"):
                    rdates = [d.dt for d in rdate_prop.dts]
                else:
                    for item in rdate_prop:
                        if hasattr(item, "dts"):
                            rdates.extend([d.dt for d in item.dts])
                for rdt in rdates:
                    occ = _normalize_dt(rdt)
                    if window_start <= occ <= window_end:
                        occurrences.add(occ)

            if not occurrences:
                occurrences.add(start)

            if exdate_prop:
                exdates = []
                if hasattr(exdate_prop, "dts"):
                    exdates = [d.dt for d in exdate_prop.dts]
                else:
                    for item in exdate_prop:
                        if hasattr(item, "dts"):
                            exdates.extend([d.dt for d in item.dts])
                exdates = {_normalize_dt(d) for d in exdates}
                occurrences = {occ for occ in occurrences if occ not in exdates}

            for occ_start in sorted(occurrences):
                if not (window_start <= occ_start <= window_end):
                    continue

                occ_end = occ_start + duration if duration else None
                occ_uid = uid
                if rrule_prop or rdate_prop:
                    occ_uid = f"{uid}:{occ_start.isoformat()}"

                uids_in_feed.add(occ_uid)

                TrainingEvent.objects.update_or_create(
                    uid=occ_uid,
                    defaults={
                        "title": summary,
                        "description": description,
                        "location": location,
                        "status": status_value,
                        "is_active": status_value == "confirmed",
                        "start": occ_start,
                        "end": occ_end,
                    },
                )

        TrainingEvent.objects.filter(start__gte=window_start).exclude(
            uid__in=uids_in_feed
        ).update(is_active=False)
