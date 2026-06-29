
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import(
    Ball, MatchState, BattingStats, BowlingStats, 
)
from .serializers import(
    StartInningsSerializer, BallEntrySerializer,
    BallSerializer, MatchStateSerializer, BattingStatsSerializer,
    BowlingStatsSerializer
)

from .permissions import IsAdminOrScorer
from matches.models import(
    Match, PlayingXI
)
from authsystem.models import UserProfile



class StartInningsView(APIView):
    permission_classes = [IsAdminOrScorer]

    def post(self, request):
        serializer = StartInningsSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status= status.HTTP_400_BAD_REQUEST
            )
        
        match = serializer.validated_data["match_obj"]
        striker_id = serializer.validated_data["striker"]
        non_striker_id = serializer.validated_data["non_striker"]
        bowler_id = serializer.validated_data["bowler"]

        match_state, created = MatchState.objects.get_or_create(match = match)

        if not created:
            if match_state.current_innings == 1:
                match_state.innings1_runs = match_state.total_runs
                match_state.innings1_wickets = match_state.total_wickets
                match_state.innings1_balls = match_state.total_balls
                match_state.current_innings = 2
                
            #reset all score for new innings :
            match_state.total_runs = 0
            match_state.total_wickets = 0
            match_state.total_balls = 0
            
        match_state.striker_id = striker_id
        match_state.non_striker_id = non_striker_id
        match_state.current_bowler_id = bowler_id
        match_state.is_active = True
        match_state.save()

        return Response(
            MatchStateSerializer(match_state).data,
            status= status.HTTP_200_OK
        )

            