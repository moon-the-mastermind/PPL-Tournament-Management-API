import uuid
from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Admin manual-vabe captain assign korbe, tai null=True rakha hoyeche
    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_teams'
    )
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)  # Payment success hole True hobe
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Invitation(models.Model):
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        related_name='invitations'
    )
    # Unique token generate hobe player join korar jonno
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usage_limit = models.PositiveIntegerField(default=15)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Token valid kina check korar logic
        return self.is_active and self.used_count < self.usage_limit

    def __str__(self):
        return f"Invite for {self.team.name} ({self.used_count}/{self.usage_limit})"
