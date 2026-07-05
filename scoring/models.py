from django.db import models
from authsystem.models import TimeStampedModel


class Ball(TimeStampedModel):
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='balls')
    innings = models.PositiveIntegerField(choices=((1, 'Innings 1'), (2, 'Innings 2')))
    over = models.PositiveIntegerField()
    ball_num = models.PositiveIntegerField()

    batsman = models.ForeignKey('authsystem.UserProfile', on_delete=models.CASCADE, related_name='balls_faced')
    non_striker = models.ForeignKey('authsystem.UserProfile', on_delete=models.CASCADE, related_name='partner_balls')
    bowler = models.ForeignKey('authsystem.UserProfile', on_delete=models.CASCADE, related_name='balls_bowled')

    runs = models.PositiveIntegerField(default=0)
    EXTRAS_CHOICES = (
        ('none', 'None'),
        ('wd', 'Wide'),
        ('nb', 'No Ball'),
        ('lb', 'Leg Bye'),
        ('b', 'Bye'),
    )
    extra_type = models.CharField(max_length=10, choices=EXTRAS_CHOICES, default='none')
    extra_runs = models.PositiveIntegerField(default=0)

    is_wicket = models.BooleanField(default=False)
    wicket_type = models.CharField(max_length=50, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['innings', 'over', 'ball_num']

    def __str__(self):
        return f"Match {self.match.id} - {self.over}.{self.ball_num}"


class MatchState(TimeStampedModel):
    match = models.OneToOneField('matches.Match', on_delete=models.CASCADE, related_name='live_state')

    current_innings = models.PositiveIntegerField(default=1)
    striker = models.ForeignKey('authsystem.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_striking')
    non_striker = models.ForeignKey('authsystem.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_non_striking')
    current_bowler = models.ForeignKey('authsystem.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_bowling')

    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    total_balls = models.PositiveIntegerField(default=0)

    current_rr = models.FloatField(default=0.0)

    innings1_runs = models.PositiveIntegerField(default=0)
    innings1_wickets = models.PositiveIntegerField(default=0)
    innings1_balls = models.PositiveIntegerField(default=0)
    innings1_rr = models.FloatField(default=0.0)

    innings2_runs = models.PositiveIntegerField(default=0)
    innings2_wickets = models.PositiveIntegerField(default=0)
    innings2_balls = models.PositiveIntegerField(default=0)
    innings2_rr = models.FloatField(default=0.0)

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

    overs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    maiden_overs = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.full_name} - {self.wickets}/{self.runs_conceded}"