
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

class BallEntryView(APIView):
    permission_classes = [IsAdminOrScorer]

    @transaction.automic
    def post(self, request):
        serializer = BallEntrySerializer(data = request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status= status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        match = get_object_or_404(Match, id = data['match'])
        match_state = get_object_or_404(MatchState, match= match)

        if not match_state.is_active:
            return Response(
                {
                    "error" : "This innings is not active right now."
        
                },
                status= status.HTTP_400_BAD_REQUEST
            )
        
        runs = data['runs']
        extra_type = data['extra_type']
        extra_runs = data['extra_runs']
        is_wicket = data['is_wicket']
        wicket_type = data.get('wicket_type')
        out_player_id = data.get('out_player')
        new_bowler_id = data.get('new_bowler')

        striker = match_state.striker
        non_striker = match_state.non_striker
        bowler = match_state.current_bowler

        if not striker or not non_striker or not bowler:
            return Response(
                {"error" : "Striker or Non-striker or Bowler are not set. Start a innings first."},
                status= status.HTTP_400_BAD_REQUEST
            )
        
        #find over and ball number
        current_over = match_state.total_balls // 6
        current_ball_in_over = match_state.total_balls % 6
        
        #wide/no ball are not legally countable
        is_legal_ball = extra_type not in ['wd', 'nb']
        ball_num_display = current_ball_in_over + 1 if is_legal_ball else current_ball_in_over


        #create ball record:
        Ball.objects.create(
            match = match,
            innings = match_state.current_innings,
            over = current_over,
            ball_num = ball_num_display if ball_num_display > 0 else 1,
            batsman = striker,
            bowler = bowler,
            runs = runs,
            extra_type = extra_type,
            extra_runs = extra_runs,
            is_wicket = is_wicket,
            wicket_type = wicket_type if is_wicket else None
        )

        #matchState update:

        total_runs_this_ball = runs + extra_runs
        match_state.total_runs += total_runs_this_ball

        if is_legal_ball:
            match_state.total_balls += 1
        if is_wicket:
            match_state.total_wickets += 1

        #batting states update :
        if extra_type not in ["wd"]:
            batting_stats, _ = BattingStats.objects.get_or_create(match= match, player = striker, defaults= {"team" : self._get_player_team(striker, match)})

            if extra_type not in ['lb', 'b']:
                batting_stats.runs += runs
            if extra_type != 'nb' or True:
                batting_stats.balls += 1
            if runs == 4:
                batting_stats.fours += 1
            if runs == 6:
                batting_stats.sixes += 1

        #bowling states:
        bowling_states, _ = BowlingStats.objects.get_or_create(
            match = match, player = bowler,
            defaults = {"team" : self._get_player_team(bowler, match)}
        )
        bowling_states.runs_conceded += total_runs_this_ball
        if is_legal_ball:
            balls_bowled = int(bowling_states.overs * 10) % 10 +1
            over_completed = int(bowling_states.overs)

            if balls_bowled >=6:
                bowling_states.overs = over_completed + 1
            else:
                bowling_states.overs = over_completed + (balls_bowled / 10)


        # if wicket:
        if is_wicket:
            bowling_states.wickets += 1
            out_player = striker
            if out_player_id:
                out_player = get_object_or_404(UserProfile, id = out_player_id) if out_player_id != striker.id else striker
        
            out_batting_stats, _ = BattingStats.objects.get_or_create(
                match = match, player = out_player,
                defaults= {"team" : self._get_player_team(out_player, match)}
            )

            out_batting_stats.is_out = True
            out_batting_stats.wicket_type = wicket_type
            out_batting_stats.save()
        
        #strike rotation
        if not is_wicket:
            if runs in [1, 3]:
                match_state.striker_id, match_state.non_striker_id = match_state.non_striker_id, match_state.striker_id

        
        #over sesh hole logic likhte hobe : 
        if is_legal_ball and match_state.total_balls % 6 == 0 and match_state.total_balls > 0:
            match_state.striker_id, match_state.non_striker_id = match_state.non_striker_id, match_state.striker_id
            if new_bowler_id:
                match_state.current_bowler_id = new_bowler_id
        
        if extra_type not in ['wd']:
            batting_stats.save()
        bowling_states.save()
        match_state.save()
        
        return Response(
            {
                "message" : "Ball recorded succeesfully.",
                "match_state" : MatchStateSerializer(match_state).data
            },
            status= status.HTTP_201_CREATED
        )
    def _get_player_team(self, player, match):
        playing_xi = PlayingXI.objects.filter(match= match, player = player).first()
        return playing_xi.team if playing_xi else None



class MatchStateView(generics.RetrieveAPIView):
    serializer_class = MatchStateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "match_id"
    
    def get_object(self):
        match_id - self.kwargs.get("match_id")
        return get_object_or_404(MatchState, match_id = match_id)
    































