from django.urls import path
from .views import (
    TournamentListCreateView,
    TournamentDetailView,
    MatchListCreateView,
    MatchDetailView,
    MatchUpdateView,
    TossUpdateView,
    MatchStatusUpdateView,
    PlayingXIListCreateView,
    PlayingXIDetailView,
)

urlpatterns = [
    # Tournament
    path('tournaments/', TournamentListCreateView.as_view(), name='tournament_list_create'),
    path('tournaments/<int:id>/', TournamentDetailView.as_view(), name='tournament_detail'),

    # Match
    path('list/', MatchListCreateView.as_view(), name='match_list_create'),
    path('details/<int:id>/', MatchDetailView.as_view(), name='match_detail'),
    path('update/<int:id>/', MatchUpdateView.as_view(), name='match_update'),
    path('toss/<int:id>/', TossUpdateView.as_view(), name='match_toss'),
    path('status/<int:id>/', MatchStatusUpdateView.as_view(), name='match_status'),

    # PlayingXI
    path('playing-xi/', PlayingXIListCreateView.as_view(), name='playing_xi_list_create'),
    path('playing-xi/<int:id>/', PlayingXIDetailView.as_view(), name='playing_xi_detail'),
]