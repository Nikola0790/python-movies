from rest_framework import serializers
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

    class Meta:
        model = Cinema
        fields = ["id", "name", "city", "movies"]


class ScreeningSerializer(serializers.ModelSerializer):

    movie = serializers.StringRelatedField()
    cinema = serializers.StringRelatedField()

    class Meta:
        model = Screening
        fields = ["id", "movie", "cinema", "date"]
