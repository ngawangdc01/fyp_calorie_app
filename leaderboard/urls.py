from django.urls import path
from . import views

urlpatterns = [
    # path('', views.leaderboard, name='leaderboard'),
    path('', views.leaderboard_view, name='leaderboard'),
    path('toggle-leaderboard/', views.toggle_leaderboard_visibility, name='toggle_leaderboard'),
]