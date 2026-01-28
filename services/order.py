from django.db import transaction
from django.db.models import QuerySet

from db.models import Order, Ticket, User


def create_order(
        tickets: list[dict],
        username: User,
        date: str = None,
) -> Order:
    with transaction.atomic():
        user = User.objects.get(username=username)

        if date:
            order = Order.objects.create(
                created_at=date,
                user=user
            )
        else:
            order = Order.objects.create(user=user)

        for ticket_data in tickets:
            Ticket.objects.create(
                order=order,
                movie_session=ticket_data["move_session"],
                title=ticket_data["title"],
                row=ticket_data["row"],
                seat=ticket_data["seat"]
            )
        return order


def get_user(username : str = None) -> QuerySet:
    if username:
        return Order.objects.filter(user__username=username)
    return Order.objects.all()
