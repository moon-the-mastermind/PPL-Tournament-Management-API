
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = True, style = {"input_type" : "password"})

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validate_data):
        user = User.objects.create_user(
            username = validate_data['username'],
            email= self.validated_data['email'],
            password= validate_data['password'],
            role = validate_data.get("role", "viewer"),  
        )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "role"]


class PublicProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    playing_info = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id", "username", "user_role", "full_name", 
            "image", "bio", "playing_info"
        ]

    def get_playing_info(self, obj):
        try:
            membership = obj.team_membership
            return {
                "team_name": membership.team.name,
                "role": membership.role,
                "jersey_number": membership.jersey_number,
                "batting_style": membership.batting_style,
                "bowling_style": membership.bowling_style,
            }
        except AttributeError:
            return None
        
        
class PrivateProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    playing_info = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id", "username", "email", "user_role", "full_name", 
            "ssc_batch", "phone_number", "image", "bio",
            "address", "date_of_birth", "playing_info", 
            "created_at", "updated_at"
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_playing_info(self, obj):
        try:
            membership = obj.team_membership
            return {
                "team_name": membership.team.name,
                "role": membership.role,
                "jersey_number": membership.jersey_number,
                "batting_style": membership.batting_style,
                "bowling_style": membership.bowling_style,
            }
        except AttributeError:
            return None

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance