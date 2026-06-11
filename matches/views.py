from .permissions import IsadminUser, IsAdminOrReadOnly
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Tournament, Match, PlayingXI
from .serializers import TournamentSerializers, MatchSerializer, PlayingXISerializer
from django_filters.rest_framework import DjangoFilterBackend


class TournamentListCreateView(generics.ListCreateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializers
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"


class TournamentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializers
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"


class MatchListCreateView(generics.ListCreateAPIView):
    serializer_class = MatchSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "tournament", "team1", "team2"]

    def get_queryset(self):
        return Match.objects.select_related(
            "tournament", "team1", "team2",
            "toss_winner", "batting_first", "winner"
        ).all()


class MatchDetailView(generics.RetrieveAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Match.objects.select_related(
            "tournament", "team1", "team2",
            "toss_winner", "batting_first", "winner"
        ).all()


class MatchUpdateView(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsadminUser]
    lookup_field = "id"


class TossUpdateView(APIView):
    permission_classes = [IsadminUser]

    def patch(self, request, id):
        match = get_object_or_404(Match, id=id)

        if match.status != "upcoming":
            return Response(
                {"error": "Toss only can be changed for upcoming match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        toss_winner_id = request.data.get("toss_winner")
        batting_first_id = request.data.get("batting_first")

        if not toss_winner_id or not batting_first_id:
            return Response(
                {"error": "Toss winner and Batting first both are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if toss_winner_id not in [match.team1.id, match.team2.id]:
            return Response(
                {"error": "Toss winner team not in this match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if batting_first_id not in [match.team1.id, match.team2.id]:
            return Response(
                {"error": "Batting first team not in this match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        match.toss_winner_id = toss_winner_id
        match.batting_first_id = batting_first_id
        match.save()

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_200_OK
        )


class MatchStatusUpdateView(APIView):
    permission_classes = [IsadminUser]

    VALID_TRANSITIONS = {
        'upcoming': 'live',
        'live': 'finished',
    }

    def patch(self, request, id):
        match = get_object_or_404(Match, id=id)
        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"error": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed = self.VALID_TRANSITIONS.get(match.status)
        if new_status != allowed:
            return Response(
                {"error": f"Can't move from '{match.status}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status == "finished":
            winner_id = request.data.get("winner")

            if not winner_id:
                return Response(
                    {"error": "You must assign winner before finishing the match."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if winner_id not in [match.team1.id, match.team2.id]:
                return Response(
                    {"error": "Winner team doesn't exist in this match."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            match.winner_id = winner_id

        match.status = new_status
        match.save()

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_200_OK
        )


class PlayingXIListCreateView(generics.ListCreateAPIView):
    serializer_class = PlayingXISerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["match", "team"]

    def get_queryset(self):
        return PlayingXI.objects.select_related(
            "match", "team", "player"
        ).all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        team = serializer.validated_data.get("team")

        if user.role != "admin" and team.captain != user:
            raise permissions.PermissionDenied(
                "Only admin and captain can submit playing XI."
            )
        serializer.save()


class PlayingXIDetailView(generics.RetrieveDestroyAPIView):
    queryset = PlayingXI.objects.all()
    serializer_class = PlayingXISerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"