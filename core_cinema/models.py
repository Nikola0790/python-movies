from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    def __str__(self):
        return self.title


class MovieStuff(models.Model):
    ROLE_CHOICES = [
        ("ACTOR", "Actor"),
        ("DIRECTOR", "Director"),
        ("WRITER", "Writer"),
    ]

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    movies = models.ManyToManyField(Movie, related_name="cast_and_crew", blank=True)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.get_role_display()})"


class Cinema(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    movies = models.ManyToManyField(Movie, through="Screening", related_name="cinemas")

    def __str__(self):
        return f"{self.name} ({self.city})"


class Screening(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="screenings"
    )
    cinema = models.ForeignKey(
        Cinema, on_delete=models.CASCADE, related_name="screenings"
    )
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} at {self.cinema.name} on {self.date.strftime('%Y-%m-%d %H:%M')}"


class Customer(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    screenings = models.ManyToManyField(Screening, related_name="attendees", blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"
