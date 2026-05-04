from django.db import models
from django.conf import settings

class Ball(models.Model):
    # Proti ti boler details ekhane thakbe
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='balls')
    innings = models.PositiveIntegerField(choices=((1, 'Innings 1'), (2, 'Innings 2')))
    over = models.PositiveIntegerField() # 0 to 19
    ball_num = models.PositiveIntegerField() # 1 to 6
    
    batsman = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.CASCADE, related_name='balls_faced')
    non_striker = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.CASCADE, related_name='partner_balls')
    bowler = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.CASCADE, related_name='balls_bowled')
    
    runs = models.PositiveIntegerField(default=0) # Runs from bat
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
    wicket_type = models.CharField(max_length=50, null=True, blank=True) # Bowled, Catch, etc.
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['innings', 'over', 'ball_num']

    def __str__(self):
        return f"Match {self.match.id} - {self.over}.{self.ball_num}"

class MatchState(models.Model):
    # Live status for WebSockets
    match = models.OneToOneField('matches.Match', on_delete=models.CASCADE, related_name='live_state')
    
    current_innings = models.PositiveIntegerField(default=1)
    striker = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.SET_NULL, null=True, related_name='current_striking')
    non_striker = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.SET_NULL, null=True, related_name='current_non_striking')
    current_bowler = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.SET_NULL, null=True, related_name='current_bowling')
    
    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    total_balls = models.PositiveIntegerField(default=0) # To calculate current over
    
    is_active = models.BooleanField(default=True) # Match cholche kina

    def __str__(self):
        return f"Live State: {self.match}"

class BattingStats(models.Model):
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='batting_stats')
    player = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.CASCADE, related_name='career_batting')
    
    runs = models.PositiveIntegerField(default=0)
    balls = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)
    is_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.full_name} - {self.runs}({self.balls})"

class BowlingStats(models.Model):
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE, related_name='bowling_stats')
    player = models.ForeignKey('authsystem.PlayerProfile', on_delete=models.CASCADE, related_name='career_bowling')
    
    overs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0) # e.g., 3.4
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    maiden_overs = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.full_name} - {self.wickets}/{self.runs_conceded}"