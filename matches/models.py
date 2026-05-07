from django.db import models
from django.conf import settings
from authsystem.models import TimeStampedModel

class Tournament(TimeStampedModel):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Match(TimeStampedModel):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('finished', 'Finished'),
    )
    
    tournament = models.ForeignKey(
        Tournament, 
        on_delete=models.CASCADE, 
        related_name='matches'
    )
    team1 = models.ForeignKey(
        'teams.Team', 
        on_delete=models.CASCADE, 
        related_name='matches_as_team1'
    )
    team2 = models.ForeignKey(
        'teams.Team', 
        on_delete=models.CASCADE, 
        related_name='matches_as_team2'
    )
    
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    total_overs = models.PositiveIntegerField(default=20)
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='upcoming'
    )
    
    toss_winner = models.ForeignKey(
        'teams.Team', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='toss_wins'
    )
    
    # Kon team prothome batting korche seta track korar jonno
    batting_first = models.ForeignKey(
        'teams.Team', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='batting_first_matches'
    )
    banner = models.ImageField(upload_to='match_banners/', null=True, blank=True)

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} - {self.tournament.name}"

class PlayingXI(TimeStampedModel):
    match = models.ForeignKey(
        Match, 
        on_delete=models.CASCADE, 
        related_name='playing_eleven'
    )
    team = models.ForeignKey(
        'teams.Team', 
        on_delete=models.CASCADE, 
        related_name='match_participations'
    )
    # authsystem app-er UserProfile model k ekhane link kora hoyeche
    player = models.ForeignKey(
        'authsystem.UserProfile', 
        on_delete=models.CASCADE, 
        related_name='matches_played'
    )

    class Meta:
        # Eki match-e eki player ke jate dui bar add na kora jay
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.full_name} in {self.match}"