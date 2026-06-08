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
