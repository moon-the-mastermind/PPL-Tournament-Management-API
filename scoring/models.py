from django.db import models
from django.conf import settings
from authsystem.models import TimeStampedModel


class MatchState(TimeStampedModel):
    match = models.OneToOneField('matches.Match', on_delete=models.CASCADE, related_name='live_state')

    current_innings = models.PositiveIntegerField(default=1)
    striker = models.ForeignKey('authsystem.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_striking')
    non_striker = models.ForeignKey('authsystem.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_non_striking')
    current_bowler = models.ForeignKey('authsystem.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_bowling')

    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    total_balls = models.PositiveIntegerField(default=0)

    # Live RR — প্রতিটা ball এ auto update
    current_rr = models.FloatField(default=0.0)             # ✅ একটাই field

    # 1st innings final score (freeze হবে innings শেষে)
    innings1_runs = models.PositiveIntegerField(default=0)
    innings1_wickets = models.PositiveIntegerField(default=0)
    innings1_balls = models.PositiveIntegerField(default=0)
    innings1_rr = models.FloatField(default=0.0)            # ✅ 1st innings final RR

    # 2nd innings final score
    innings2_runs = models.PositiveIntegerField(default=0)
    innings2_wickets = models.PositiveIntegerField(default=0)
    innings2_balls = models.PositiveIntegerField(default=0)
    innings2_rr = models.FloatField(default=0.0)            # ✅ 2nd innings final RR

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Live State: {self.match}"

class BattingStats(TimeStampedModel):
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='batting_stats')
    player = models.ForeignKey('authsystem.UserProfile', on_delete=models.CASCADE, related_name='career_batting')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='batting_innings', null=True, blank=True)

    runs = models.PositiveIntegerField(default=0)
    balls = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)
    is_out = models.BooleanField(default=False)
    wicket_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.full_name} - {self.runs}({self.balls})"


class BowlingStats(TimeStampedModel):
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='bowling_stats')
    player = models.ForeignKey('authsystem.UserProfile', on_delete=models.CASCADE, related_name='career_bowling')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='bowling_innings', null=True, blank=True)

    overs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)  # e.g., 3.4
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    maiden_overs = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.full_name} - {self.wickets}/{self.runs_conceded}"