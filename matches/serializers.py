from rest_framework import serializers
from .models import(
    Tournament, Match, PlayingXI, TournamentStanding
)
from teams.models import Team

class TournamentSerializers(serializers.ModelSerializer):
    total_matches = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = [
            "id", "name", "start_date", "end_date","total_matches",
            "is_active", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def get_total_matches(self, obj):
        return obj.matches.count()

class MatchSerializer(serializers.ModelSerializer):
    tournament_name = serializers.ReadOnlyField(source = "tournament.name")
    team1_name = serializers.ReadOnlyField(source = "team1.name")
    team2_name = serializers.ReadOnlyField(source = "team2.name")
    toss_winner_name = serializers.ReadOnlyField(source = "toss_winner.name")
    batting_first_name = serializers.ReadOnlyField(source = "batting_first.name")
    winner_name = serializers.ReadOnlyField(source = "winner.name")

    class Meta:
        model = Match
        fields = [
            "id", "tournament", "tournament_name", "team1", 
            "team1_name", "team2", "team2_name", "match_date",
            "venue", "total_overs", "status", "toss_winner", "toss_winner_name", 
            "batting_first", "batting_first_name", "winner", 
            "winner_name", "banner", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
            team1 = data.get("team1")
            team2 = data.get("team2")

            if team1 and team2 and team1 == team2:
                raise serializers.ValidationError({
                    "team2" : "team1 and team2 can't be same."
                })
            return data
    
class PlayingXISerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source = "player.full_name")
    team_name = serializers.ReadOnlyField(source = "team.name")
    match_name = serializers.SerializerMethodField()

    class Meta:
        model = PlayingXI
        fields = [
              "id", "match", "match_name",
              "team", "team_name", "player", 
              "player_name", "created_at"
        ]
        read_only_fields = ['id', 'created_at']

    def get_match_name(self, obj):
        return f"{obj.match.team1.name} V/S {obj.match.team2.name}"
    
    def validate(self, data):
        match = data.get("match")
        team = data.get("team")
        player = data.get("player")


        #check is the team is for this match
        if team not in [match.team1, match.team2]:
            raise serializers.ValidationError(
                {
                    "team" : "This team is not exist in this match."
                }
            )
        
        #check is the member exists in this team.
        if not team.team_members.filter(player=player).exists():
            raise serializers.ValidationError(
                {
                    "player" : "this player is not assigned in this team."
                }
            )
        
        #check and set playable member 8 or not
        existing_count = PlayingXI.objects.filter(
            match = match, team = team
        ).count()
        if existing_count >=8:
            raise serializers.ValidationError(
                {
                    "team" : "Only 8 players are allowed to play."
                }
            )
        return data

class TournamentStandingSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source = "team.name")
    team_logo = serializers.ImageField(source = "team.logo", read_only = True)
    tournament_name = serializers.ReadOnlyField(source = "tournament.name")

    class Meta:
        model = TournamentStanding
        fields = [
            'id', 'tournament', 'tournament_name',
            'team', 'team_name', 'team_logo',
            'match_played', 'won', 'lost',
            'points', 'nrr',
            'runs_scored', 'balls_faced',     
            'runs_conceded', 'balls_bowled',    
        ] 
        read_only_fields = ['id'] 

        
            


        

         
    
        
