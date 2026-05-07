from django.db import models
from django.contrib.auth.models import AbstractUser
# from teams.models import Team



class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    updated_at = models.DateTimeField(auto_now=True, null = True, blank = True)

    class Meta:
        abstract = True

class User(AbstractUser, TimeStampedModel):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('scorer', 'Scorer'),
        ('captain', 'Captain'),
        ('player', 'Player'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt', 'argon2')):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}-({self.role})"

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    ssc_batch = models.CharField(max_length=4, blank=True, null=True) # Example: 2012
    image = models.ImageField(upload_to='players/', null=True, blank=True)
    bio = models.TextField(null= True, blank=True)
    def __str__(self):
        return f"{self.full_name}"
    
