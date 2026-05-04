
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PlayerProfile

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


class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source= "user.username", read_only = True)
    email = serializers.EmailField(source = "user.email", read_only = True )
    role = serializers.CharField(source= "user.role", read_only = True)
    class Meta:
        model = PlayerProfile
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.date_of_birth = validated_data.get("date_of_birth", instance.date_of_birth)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.jersey_number = validated_data.get("jersey_number", instance.jersey_number)
        instance.address = validated_data.get("address", instance.address)
        instance.role = validated_data.get("role", instance.role)
        instance.batting_style = validated_data.get("batting_style", instance.batting_style)
        instance.bowling_style = validated_data.get("bowling_style", instance.bowling_style)
        instance.image = validated_data.get("image", instance.image)

        if "image" in validated_data:
            instance.image = validated_data.get("image", instance.image)

        instance.save()
        return instance
    
    
