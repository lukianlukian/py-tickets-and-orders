from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Movie(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    actors = models.ManyToManyField(to=Actor, related_name="movies")
    genres = models.ManyToManyField(to=Genre, related_name="movies")

    def __str__(self) -> str:
        return self.title


class CinemaHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

class MovieSession(models.Model):
    show_time = models.DateTimeField()
    cinema_hall = models.ForeignKey(
        to=CinemaHall, on_delete=models.CASCADE, related_name="movie_sessions"
    )
    movie = models.ForeignKey(
        to=Movie, on_delete=models.CASCADE, related_name="movie_sessions"
    )

    def __str__(self) -> str:
        return f"{self.movie.title} {str(self.show_time)}"

class Ticket(models.Model):
    movie_session = models.ForeignKey(
        "MovieSession",
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    def clean(self):
        if not self.movie_session or not self.movie_session.cinema_hall:
            raise ValidationError("Movie session and cinema hall must be set")

        cinema_hall = self.movie_session.cinema_hall


        if not (1 <= self.row <= cinema_hall.rows):
            raise ValidationError(
                f"Row must be between 1 and {cinema_hall.rows}"
            )

        if not (1 <= self.seat <= cinema_hall.seats_in_row):
            raise ValidationError(
                f"Seat must be between 1 and {cinema_hall.seats_in_row}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "movie_session"],
                name="unique_movie_session",
            )
        ]

    def __str__(self) -> str:
        return f"{self.movie_session} {self.row} {self.seat}"


class User(AbstractUser):
    ...
