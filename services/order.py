from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.utils.dateparse import parse_datetime

from db.models import Order, Ticket


def create_order(
        tickets: list[dict],
        username: str,
        date: str = None,
) -> Order:
    user = get_user_model()

    with transaction.atomic():
        user = user.objects.get(username=username)

        order = Order.objects.create(user=user)

        if date:
            order.created_at = parse_datetime(date)
            order.save(update_fields=["created_at"])

        for ticket_data in tickets:
            Ticket.objects.create(
                order=order,
                movie_session_id=ticket_data["movie_session"],
                row=ticket_data["row"],
                seat=ticket_data["seat"],
            )

        return order


def get_orders(username: str = None) -> QuerySet:
    if username:
        return Order.objects.filter(user__username=username)
    return Order.objects.all()
