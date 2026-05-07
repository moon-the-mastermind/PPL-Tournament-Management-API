from django.urls import path
from .views import GenerateInvitationView, JoinTeamView, TeamDetailUpdateView, TeamDetailView, TeamListView, TeamMemberListView, TeamMemberDetailView

urlpatterns = [
    path("list/", TeamListView.as_view(), name = "team_list"),
    path("details/<int:id>/", TeamDetailView.as_view(), name = "team_details"),
    path('update/<int:id>/', TeamDetailUpdateView.as_view(), name='team_update'),
    path('invite/<int:team_id>/', GenerateInvitationView.as_view(), name='generate_nvite'),
    path('join/', JoinTeamView.as_view(), name='join-team'),
    path("members/", TeamMemberListView.as_view(), name = "member_list"),
    path("member/<int:id>/", TeamMemberDetailView.as_view(), name = "team_member_details")
]