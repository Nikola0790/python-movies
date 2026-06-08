from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Cinema, Screening


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "description", "duration"]


class CinemaSerializer(serializers.ModelSerializer):

    movies = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="movie-detail",
    )

    upcoming_movies = serializers.SerializerMethodField()

    class Meta:
        model = Cinema
        fields = ["id", "name", "city", "movies", 'upcoming_movies']

    def get_upcoming_movies(self, obj):
        now = timezone.now()
        fifteen_days_later = now + timedelta(days=15)

        movies_next_15_days = Movie.objects.filter(
            screenings__cinema = obj,
            screenings__date__range = (now, fifteen_days_later)
        ).distinct()

        return [movie.title for movie in movies_next_15_days]


class ScreeningSerializer(serializers.ModelSerializer):

    class Meta:
        model = Screening
        fields = ["id", "movie", "cinema", "date"]
        # By removing StringRelatedField from the top, 'movie' and 'cinema'
        # are now writable integer fields again by default!

    def to_representation(self, instance):
        """
        This method handles GET responses. We intercept the normal output
        and replace the raw IDs with clean string names for the frontend.
        """
        representation = super().to_representation(instance)

        # Swap the integer IDs out for strings dynamically
        representation["movie"] = str(instance.movie)
        representation["cinema"] = str(instance.cinema)

        return representation
