from django.urls import path
from .views import(
    StartInningsView,
    BallEntryView,
    MatchStateView,
    BallHistoryView,
    ScorecardView
)

urlpatterns = [
    path("start-innings/", StartInningsView.as_view(), name="start_innings"),
    path("ball-entry/", BallEntryView.as_view(), name = "ball_entry"),
    path("state/<int:match_id>/", MatchStateView.as_view(), name = "match_state"),
    path("history/<int:match_id/>", BallHistoryView.as_view(), name = "ball_history"),
    path("scorecard/<int:match_id>/", ScorecardView.as_view(), name = "scorecard")
]