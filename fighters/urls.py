from django.urls import path
from .views import TournamentEventsView,TwitchUserOnline,TournamentDetailsChallongeView,StarGGTournamentListView, ChallongeTournamentListView, PostListView

app_name = 'fighters'  # Asegúrate de que 'fighters' sea una cadena

urlpatterns = [
    path('tournament-events/', TournamentEventsView.as_view(), name='tournament-events'),  # Cambia el nombre de la ruta
    path('tournament/<str:tournament_id>/', TournamentDetailsChallongeView.as_view(), name='tournament-challonge-details'),
    path('stargg-tournaments/', StarGGTournamentListView.as_view(), name='stargg-tournament-list'),
    path('challonge-tournaments/', ChallongeTournamentListView.as_view(), name='challonge-tournament-list'),
    path('stream-online/', TwitchUserOnline.as_view(), name='stream-online'),
    path('posts/', PostListView.as_view(), name='post-list'),
    
]
