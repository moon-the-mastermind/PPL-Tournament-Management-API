from rest_framework import serializers
from .models import Ball, MatchState, BattingStats, BowlingStats
from authsystem.models import UserProfile


class StartInningsSerializer(serializers.Serializer):
    match = serializers.IntegerField()
    striker = serializers.IntegerField()
    non_striker = serializers.IntegerField()
    bowler = serializers.IntegerField()

    def validate(self, data):
        from matches.models import Match, PlayingXI

        match_id = data.get('match')
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise serializers.ValidationError({"match": "Match doesn't found."})

        if match.status != 'live':
            raise serializers.ValidationError({"match": "Match status must be 'live' "})

        striker_id = data.get('striker')
        non_striker_id = data.get('non_striker')
        bowler_id = data.get('bowler')

        if striker_id == non_striker_id:
            raise serializers.ValidationError({"striker": "Striker & Non-striker can't be same."})

        # striker, non_striker একই team এর হতে হবে এবং PlayingXI তে থাকতে হবে
        playing_player_ids = PlayingXI.objects.filter(match=match).values_list('player_id', flat=True)

        if striker_id not in playing_player_ids:
            raise serializers.ValidationError({"striker": "This player is not exists in this match. Add him in Playing-XI and try again."})

        if non_striker_id not in playing_player_ids:
            raise serializers.ValidationError({"non_striker": "This player is not exists in this match. Add him in Playing-XI and try again."})

        if bowler_id not in playing_player_ids:
            raise serializers.ValidationError({"bowler": "This bowler is not exists in this match. Add him in Playing-XI and try again."})

        # striker/non-striker এবং bowler ভিন্ন team এর হতে হবে — সেটা আলাদাভাবে চেক করব views এ
        data['match_obj'] = match
        return data


class BallSerializer(serializers.ModelSerializer):
    batsman_name = serializers.ReadOnlyField(source='batsman.full_name')
    bowler_name = serializers.ReadOnlyField(source='bowler.full_name')

    class Meta:
        model = Ball
        fields = [
            'id', 'match', 'innings', 'over', 'ball_num',
            'batsman', 'batsman_name', 'non_striker', 'bowler', 'bowler_name',
            'runs', 'extra_type', 'extra_runs',
            'is_wicket', 'wicket_type', 'timestamp'
        ]
        read_only_fields = ['id', 'innings', 'over', 'ball_num', 'timestamp']


class BallEntrySerializer(serializers.Serializer):
    """ Scorer যা পাঠাবে একটা বলের জন্য """
    match = serializers.IntegerField()
    runs = serializers.IntegerField(min_value=0, max_value=6, default=0)
    extra_type = serializers.ChoiceField(
        choices=['none', 'wd', 'nb', 'lb', 'b'], default='none'
    )
    extra_runs = serializers.IntegerField(min_value=0, default=0)
    is_wicket = serializers.BooleanField(default=False)
    wicket_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    # উইকেট হলে কে out হয়েছে (striker বা non-striker — run-out এর জন্য জরুরি)
    out_player = serializers.IntegerField(required=False, allow_null=True)
    # over শেষে নতুন bowler আসবে কিনা
    new_bowler = serializers.IntegerField(required=False, allow_null=True)
    new_batsman = serializers.IntegerField(required=False, allow_null=True) 


class MatchStateSerializer(serializers.ModelSerializer):
    striker_name = serializers.ReadOnlyField(source='striker.full_name')
    non_striker_name = serializers.ReadOnlyField(source='non_striker.full_name')
    bowler_name = serializers.ReadOnlyField(source='current_bowler.full_name')
    current_over = serializers.SerializerMethodField()
    current_over_balls = serializers.SerializerMethodField()

    class Meta:
        model = MatchState
        fields = [
            'id', 'match', 'current_innings',
            'striker', 'striker_name',
            'non_striker', 'non_striker_name',
            'current_bowler', 'bowler_name',
            'total_runs', 'total_wickets', 'total_balls',
            'current_over', 'current_over_balls',
            'current_rr',                                   
            'innings1_runs', 'innings1_wickets', 'innings1_balls', 'innings1_rr',
            'innings2_runs', 'innings2_wickets', 'innings2_balls', 'innings2_rr',
            'is_active'
        ]

    def get_current_over(self, obj):
        return obj.total_balls // 6

    def get_current_over_balls(self, obj):
        return obj.total_balls % 6


class BattingStatsSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='player.full_name')
    team_name = serializers.ReadOnlyField(source='team.name')
    strike_rate = serializers.SerializerMethodField()

    class Meta:
        model = BattingStats
        fields = [
            'id', 'match', 'player', 'player_name', 'team', 'team_name',
            'runs', 'balls', 'fours', 'sixes', 'is_out', 'wicket_type',
            'strike_rate'
        ]

    def get_strike_rate(self, obj):
        if obj.balls == 0:
            return 0.0
        return round((obj.runs / obj.balls) * 100, 2)


class BowlingStatsSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='player.full_name')
    team_name = serializers.ReadOnlyField(source='team.name')
    economy = serializers.SerializerMethodField()

    class Meta:
        model = BowlingStats
        fields = [
            'id', 'match', 'player', 'player_name', 'team', 'team_name',
            'overs', 'runs_conceded', 'wickets', 'maiden_overs',
            'economy'
        ]

    def get_economy(self, obj):
        if obj.overs == 0:
            return 0.0
        return round(float(obj.runs_conceded) / float(obj.overs), 2)