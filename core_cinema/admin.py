from django.contrib import admin
from .models import Movie, MovieStuff, Cinema, Screening

@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'duration')

@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ('movie', 'cinema', 'date')

@admin.register(MovieStuff)
class MovieStuffAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'role')
    filter_horizontal = ('movies',)