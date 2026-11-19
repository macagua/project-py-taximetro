"""Template tags for the taxi stats cards in the Django admin dashboard."""

from django import template

register = template.Library()


@register.inclusion_tag("admin/stats_cards.html")
def stats_cards():
    from django.contrib.auth.models import Group
    from fleet.models import Ride

    try:
        g = Group.objects.get(name="Conductores")
        conductores_count = g.user_set.count()
    except Group.DoesNotExist:
        conductores_count = 0

    total_rides = Ride.objects.filter(status=Ride.STATUS_DONE).count()

    return {
        "conductores_count": conductores_count,
        "total_rides": total_rides,
    }
