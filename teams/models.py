import uuid
from django.db import models
from django.conf import settings
from authsystem.models import TimeStampedModel
from django.core.exceptions import ValidationError

class Team(TimeStampedModel):
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

    def clean(self):
        super().clean()
        if self.captain:
            # ডাটাবেসে রিকোয়েস্ট পাঠানোর আগেই চেক
            exists = Team.objects.filter(captain=self.captain).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError({
                    'captain': f"এই ইউজার ({self.captain.username}) ইতিমধ্যে অন্য একটি টিমের ক্যাপ্টেন।"
                })

    def __str__(self):
        return self.name

class Invitation(TimeStampedModel):
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


class TeamMember(TimeStampedModel):
    ROLE_CHOICES = [
        ('batsman', 'Batsman'),
        ('bowler', 'Bowler'),
        ('all_rounder', 'All Rounder'),
        ('wicket_keeper', 'Wicket Keeper'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    # OneToOneField নিশ্চিত করবে একজন ইউজার একটির বেশি টিমে থাকতে পারবে না
    player = models.OneToOneField(
        'authsystem.UserProfile', 
        on_delete=models.CASCADE, 
        related_name='team_membership'
    )
    
    # প্লেয়ার স্পেসিফিক ডেটা যা ভিউয়ারদের থাকবে না
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='batsman')
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    batting_style = models.CharField(max_length=50, null=True, blank=True)
    bowling_style = models.CharField(max_length=50, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.player.full_name} ({self.team.name})"