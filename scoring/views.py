
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.shortcuts import get_object_or_404
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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
    

    
def calculate_rr(runs, balls):
    if balls == 0:
        return 0.0
    overs = balls / 6
    return round(runs / overs, 2)


class BallEntryView(APIView):
    permission_classes = [IsAdminOrScorer]

    @transaction.atomic
    def post(self, request):
        serializer = BallEntrySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        match = get_object_or_404(Match, id=data['match'])
        match_state = get_object_or_404(
            MatchState.objects.select_related('striker', 'non_striker', 'current_bowler'),
            match=match
        )

        if not match_state.is_active:
            return Response(
                {"error": "This innings is not active right now."},
                status=status.HTTP_400_BAD_REQUEST
            )

        runs = data['runs']
        extra_type = data['extra_type']
        extra_runs = data['extra_runs']
        is_wicket = data['is_wicket']
        wicket_type = data.get('wicket_type')
        out_player_id = data.get('out_player')
        new_bowler_id = data.get('new_bowler')
        new_batsman_id = data.get('new_batsman')

        striker = match_state.striker
        non_striker = match_state.non_striker
        bowler = match_state.current_bowler

        if not striker or not non_striker or not bowler:
            return Response(
                {"error": "Striker, Non-striker or Bowler are not set. Please call Start Innings first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate current over and ball number
        current_over = match_state.total_balls // 6
        current_ball_in_over = match_state.total_balls % 6
        is_legal_ball = extra_type not in ['wd', 'nb']
        ball_num_display = current_ball_in_over + 1 if is_legal_ball else current_ball_in_over

        # Create ball record
        Ball.objects.create(
            match=match,
            innings=match_state.current_innings,
            over=current_over,
            ball_num=ball_num_display if ball_num_display > 0 else 1,
            batsman=striker,
            non_striker=non_striker,
            bowler=bowler,
            runs=runs,
            extra_type=extra_type,
            extra_runs=extra_runs,
            is_wicket=is_wicket,
            wicket_type=wicket_type if is_wicket else None
        )

        # Update MatchState
        total_runs_this_ball = runs + extra_runs
        match_state.total_runs += total_runs_this_ball

        if is_legal_ball:
            match_state.total_balls += 1
        if is_wicket:
            match_state.total_wickets += 1

        # Update BattingStats
        if extra_type not in ['wd']:
            batting_stats, _ = BattingStats.objects.get_or_create(
                match=match, player=striker,
                defaults={'team': self._get_player_team(striker, match)}
            )
            if extra_type not in ['lb', 'b']:
                batting_stats.runs += runs
            batting_stats.balls += 1
            if runs == 4:
                batting_stats.fours += 1
            if runs == 6:
                batting_stats.sixes += 1

        # Update BowlingStats
        bowling_stats, _ = BowlingStats.objects.get_or_create(
            match=match, player=bowler,
            defaults={'team': self._get_player_team(bowler, match)}
        )
        bowling_stats.runs_conceded += total_runs_this_ball
        if is_legal_ball:
            balls_bowled = int(bowling_stats.overs * 10) % 10 + 1
            overs_completed = int(bowling_stats.overs)
            if balls_bowled >= 6:
                bowling_stats.overs = overs_completed + 1
            else:
                bowling_stats.overs = overs_completed + (balls_bowled / 10)

        # Handle wicket
        if is_wicket:
            bowling_stats.wickets += 1

            out_player = striker
            if out_player_id and out_player_id != striker.id:
                out_player = get_object_or_404(UserProfile, id=out_player_id)

            out_batting_stats, _ = BattingStats.objects.get_or_create(
                match=match, player=out_player,
                defaults={'team': self._get_player_team(out_player, match)}
            )
            out_batting_stats.is_out = True
            out_batting_stats.wicket_type = wicket_type
            out_batting_stats.save()

            # Set new batsman as striker
            if new_batsman_id:
                match_state.striker_id = new_batsman_id
            else:
                match_state.striker_id = None

        # Strike rotation on odd runs
        if not is_wicket and runs in [1, 3]:
            match_state.striker_id, match_state.non_striker_id = (
                match_state.non_striker_id, match_state.striker_id
            )

        # End of over — swap strike and change bowler
        if is_legal_ball and match_state.total_balls % 6 == 0 and match_state.total_balls > 0:
            match_state.striker_id, match_state.non_striker_id = (
                match_state.non_striker_id, match_state.striker_id
            )
            if new_bowler_id:
                match_state.current_bowler_id = new_bowler_id

        # Live RR calculate — auto update on every ball
        match_state.current_rr = calculate_rr(match_state.total_runs, match_state.total_balls)

        # Save all updates
        if extra_type not in ['wd']:
            batting_stats.save()
        bowling_stats.save()
        match_state.save()

        # Check if innings or match is over
        max_balls = match.total_overs * 6
        max_wickets = match.max_wickets
        innings_over = False

        if match_state.total_wickets >= max_wickets:
            innings_over = True
        if match_state.total_balls >= max_balls:
            innings_over = True
        if match_state.current_innings == 2:
            target = match_state.innings1_runs + 1
            if match_state.total_runs >= target:
                innings_over = True

        if innings_over:
            match_state.is_active = False

            # End of 1st innings
            if match_state.current_innings == 1:
                match_state.innings1_runs = match_state.total_runs
                match_state.innings1_wickets = match_state.total_wickets
                match_state.innings1_balls = match_state.total_balls
                match_state.innings1_rr = match_state.current_rr  # ✅ freeze 1st innings RR
                match_state.current_rr = 0.0                       # ✅ reset for 2nd innings
                match_state.save()

                return Response(
                    {
                        "message": "1st innings completed! Please start the 2nd innings.",
                        "innings1_runs": match_state.innings1_runs,
                        "innings1_wickets": match_state.innings1_wickets,
                        "innings1_balls": match_state.innings1_balls,
                        "innings1_rr": match_state.innings1_rr,
                        "match_state": MatchStateSerializer(match_state).data
                    },
                    status=status.HTTP_200_OK
                )

            # End of 2nd innings — match finished
            if match_state.current_innings == 2:
                match_state.innings2_runs = match_state.total_runs
                match_state.innings2_wickets = match_state.total_wickets
                match_state.innings2_balls = match_state.total_balls
                match_state.innings2_rr = match_state.current_rr  # ✅ freeze 2nd innings RR
                match_state.save()

                if match_state.total_runs >= match_state.innings1_runs + 1:
                    winner = match.team2 if match.batting_first == match.team1 else match.team1
                else:
                    winner = match.batting_first

                match.status = 'finished'
                match.winner = winner
                match.save()


                return Response(
                    {
                        "message": "Match finished!",
                        "winner": winner.name,
                        "innings1_runs": match_state.innings1_runs,
                        "innings1_wickets": match_state.innings1_wickets,
                        "innings1_rr": match_state.innings1_rr,
                        "innings2_runs": match_state.innings2_runs,
                        "innings2_wickets": match_state.innings2_wickets,
                        "innings2_rr": match_state.innings2_rr,
                        "match_state": MatchStateSerializer(match_state).data
                    },
                    status=status.HTTP_200_OK
                )

        # Normal ball response
        return Response(
            {
                "message": "Ball recorded successfully.",
                "match_state": MatchStateSerializer(match_state).data
            },
            status=status.HTTP_201_CREATED
        )

    def _get_player_team(self, player, match):
        playing_xi = PlayingXI.objects.filter(match=match, player=player).first()
        return playing_xi.team if playing_xi else None
    
    def _broadcast_match_team(self, match_state):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"macth_{match_state.match_id}",
            {
                "type" : "match_update",
                "data" : MatchStateSerializer(match_state).data
            }
        )


class MatchStateView(generics.RetrieveAPIView):
    serializer_class = MatchStateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "match_id"
    
    def get_object(self):
        match_id = self.kwargs.get('match_id')
        return get_object_or_404(MatchState, match_id=match_id)

    

class BallHistoryView(generics.ListAPIView):
    serializer_class = BallSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        match_id = self.kwargs.get('match_id')
        return Ball.objects.filter(match_id=match_id)



class ScorecardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, match_id):
        batting = BattingStats.objects.filter(match_id=match_id).select_related('player', 'team')
        bowling = BowlingStats.objects.filter(match_id=match_id).select_related('player', 'team')

        return Response({
            "batting": BattingStatsSerializer(batting, many=True).data,
            "bowling": BowlingStatsSerializer(bowling, many=True).data
        })

























