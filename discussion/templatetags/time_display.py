from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def compact_time(value):
    now = timezone.now()

    if not value:
        return ""

    delta = now - value

    if delta < timedelta(minutes=1):
        return "Just now"
    elif delta < timedelta(hours=1):
        return f"{int(delta.total_seconds() // 60)}m"
    elif delta < timedelta(days=1):
        return f"{int(delta.total_seconds() // 3600)}h"
    elif delta < timedelta(days=7):
        return f"{delta.days}d"
    elif delta < timedelta(days=30):
        weeks = delta.days // 7
        return f"{weeks}w"
    elif value.year == now.year:
        return value.strftime("%b %d")  # e.g., Mar 3
    else:
        return value.strftime("%b %d, %Y")  # e.g., Mar 3, 2023