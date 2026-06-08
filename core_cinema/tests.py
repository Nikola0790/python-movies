from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Cinema, Movie, Screening


class CinemaAPITests(APITestCase):
    def setUp(self):
        self.cinema = Cinema.objects.create(name="Cineplexx", city="Belgrade")
        self.list_url = reverse("cinema-list")
        self.detail_url = reverse("cinema-detail", kwargs={"pk": self.cinema.pk})

    def test_add_cinema(self):
        """Checking if adding a new cinema works (POST request)."""
        data = {
            "name": "IMAX Theater",
            "city": "Novi Sad",
            "movies": [],
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cinema.objects.count(), 2)
        self.assertEqual(Cinema.objects.latest("id").name, "IMAX Theater")

    def test_get_cinema_list(self):
        """Checking if listing all cinemas works (GET request)."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Cineplexx")

    def test_get_cinema_detail(self):
        """Checking if a detailed cinema view works (GET single item request)."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Cineplexx")
        self.assertEqual(response.data['city'], "Belgrade")

    def test_update_cinema(self):
        """Checking if updating a cinema is working (PUT / PATCH request)."""
        updated_data = {
            "name": "Cineplexx Premium",
            "city": "Belgrade"
        }
        
        response = self.client.put(self.detail_url, updated_data, format='json')
        
        # Refresh database instance state from disk to confirm changes stuck
        self.cinema.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cinema.name, "Cineplexx Premium")

    def test_delete_cinema(self):
        """Checking removal of a cinema (DELETE request)."""
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cinema.objects.count(), 0)

    def test_upcoming_movies_15_days_filter(self):
        """
        Verifies that 'upcoming_movies' field only includes unique movie titles
        scheduled within the next 15 days.
        """
        now = timezone.now()

        # 1. Create 3 different movies
        movie_valid = Movie.objects.create(title="Inception", description="Dream thief", duration=148)
        movie_far_future = Movie.objects.create(title="Avatar 5", description="Blue aliens", duration=160)
        movie_duplicate = Movie.objects.create(title="Interstellar", description="Space travel", duration=169)

        # 2. Schedule "Inception" for tomorrow (Inside the 15-day window -> SHOULD SHOW)
        Screening.objects.create(
            cinema=self.cinema, 
            movie=movie_valid, 
            date=now + timedelta(days=1)
        )

        # 3. Schedule "Avatar 5" for 20 days from now (Outside the window -> SHOULD NOT SHOW)
        Screening.objects.create(
            cinema=self.cinema, 
            movie=movie_far_future, 
            date=now + timedelta(days=20)
        )

        # 4. Schedule "Interstellar" TWICE within the 15-day window
        # (Inside window -> SHOULD SHOW, but only ONCE)
        Screening.objects.create(
            cinema=self.cinema, 
            movie=movie_duplicate, 
            date=now + timedelta(days=5)
        )
        Screening.objects.create(
            cinema=self.cinema, 
            movie=movie_duplicate, 
            date=now + timedelta(days=12)
        )

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        upcoming_movies_list = response.data.get('upcoming_movies')

        self.assertEqual(len(upcoming_movies_list), 2)

        self.assertIn("Inception", upcoming_movies_list)
        self.assertIn("Interstellar", upcoming_movies_list)
        self.assertNotIn("Avatar 5", upcoming_movies_list)


class ScreeningAPITests(APITestCase):

    def setUp(self):
        """Set up required relationships and an initial screening instance."""
        # 1. Create a Movie and a Cinema because a Screening needs both foreign keys
        self.movie = Movie.objects.create(
            title="Inception", 
            description="A thief steals corporate secrets...", 
            duration=148
        )
        self.cinema = Cinema.objects.create(name="IMAX Theater", city="Belgrade")
        
        # 2. Create an initial screening instance for detail, update, and delete tests
        self.screening_date = timezone.now()
        self.screening = Screening.objects.create(
            movie=self.movie,
            cinema=self.cinema,
            date=self.screening_date
        )
        
        # 3. Resolve the URL routes generated by your router/basename='screening'
        self.list_url = reverse('screening-list')  # Resolves to: /screenings/
        self.detail_url = reverse('screening-detail', kwargs={'pk': self.screening.pk})  # Resolves to: /screenings/<pk>/

    def test_add_screening(self):
        """Verifying that adding a new screening works (POST)."""
        data = {
            "movie": self.movie.id,
            "cinema": self.cinema.id,
            "date": "2026-07-20T18:00:00Z"
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Screening.objects.count(), 2)

    def test_get_screening_list(self):
        """Verifying that list of all screenings works (GET)."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # If your serializer uses StringRelatedField, verify it outputs names instead of IDs!
        self.assertEqual(response.data[0]['movie'], "Inception")

    def test_get_screening_detail(self):
        """Checking if the detailed view of the screening works (GET)."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['movie'], "Inception")
        self.assertEqual(response.data['cinema'], "IMAX Theater (Belgrade)")

    def test_update_screening(self):
        """Checking if the screening update works (PUT)."""
        # Let's say we want to move the screening to a different movie
        new_movie = Movie.objects.create(title="Interstellar", description="Space exploration", duration=169)
        
        updated_data = {
            "movie": new_movie.id,
            "cinema": self.cinema.id,
            "date": self.screening_date.isoformat()
        }
        
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.screening.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.screening.movie, new_movie)

    def test_delete_screening(self):
        """Checking if the screening removal works (DELETE)."""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Screening.objects.count(), 0)

    def test_filter_screenings_by_movie_and_city(self):
        """Verifies that screenings can be filtered using URL query parameters."""
        other_movie = Movie.objects.create(title="The Dark Knight", description="Batman", duration=152)
        other_cinema = Cinema.objects.create(name="Arena Cineplex", city="Novi Sad")
        
        Screening.objects.create(
            movie=other_movie,
            cinema=other_cinema,
            date=self.screening_date
        )

        # Test filtering by Movie Title
        # Looks like: /screenings/?movie=Inception
        response = self.client.get(self.list_url, {'movie': 'Inception'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], "Inception")

        # Test filtering by Cinema City
        # Looks like: /screenings/?city=Novi Sad
        response = self.client.get(self.list_url, {'city': 'Novi Sad'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], "The Dark Knight")
        self.assertIn("Novi Sad", response.data[0]['cinema'])

        # Test filtering by Movie title and Cinema city
        # Looks like: /screenings/?movie=The+Dark+Knight&city=Novi+Sad
        response = self.client.get(self.list_url, {'movie': 'The Dark Knight', 'city': 'Novi Sad'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], "The Dark Knight")
        self.assertIn("Novi Sad", response.data[0]['cinema'])