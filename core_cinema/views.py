from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Movie, MovieStuff, Cinema, Screening
from .serializers import MovieSerializer, CinemaSerializer, ScreeningSerializer


class MovieView(APIView):
    def get(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieSerializer(movie, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MovieListView(APIView):
    def get(self, request):
        all_movies = Movie.objects.all().order_by('id')
        serializer = MovieSerializer(all_movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# THIS CAN REPLACE ALL CODE ABOVE !!!
# class MovieViewSet(viewsets.ModelViewSet):
#     # 1. "Hey DRF, whenever you need to fetch data, look at this table:"
#     queryset = Movie.objects.all().order_by('id')
    
#     # 2. "Whenever you need to convert that data to JSON or validate incoming data, use this:"
#     serializer_class = MovieSerializer

class CinemaViewSet(viewsets.ModelViewSet):
    queryset = Cinema.objects.all().order_by('name')
    serializer_class = CinemaSerializer

class ScreeningViewSet(viewsets.ModelViewSet):
    queryset = Screening.objects.all().order_by('date')
    serializer_class = ScreeningSerializer