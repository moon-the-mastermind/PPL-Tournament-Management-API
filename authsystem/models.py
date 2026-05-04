from django.db import models
from django.contrib.auth.models import AbstractUser
from teams.models import Team


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('captain', 'Captain'),
        ('player', 'Player'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    email = models.EmailField(unique=True)
    def __str__(self):
        return f"{self.username}-({self.role})"

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    # ForeignKey to Team (which will be in teams app)
    # We use a string 'teams.Team' to avoid circular import
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    
    # Personal Data
    full_name = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    # Career Data
    role = models.CharField(max_length=50, null=True, blank=True)
    batting_style = models.CharField(max_length=50, null=True, blank=True)
    bowling_style = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='players/', null=True, blank=True)

    def __str__(self):
        return f"{self.name}-{self.role}"
    
