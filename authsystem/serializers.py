# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.contrib.auth.hashers import make_password

# User = get_user_model()

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'role'] # Tomar model-e 'role' field thakle sheta add koro

#     def create(self, validated_data):
#         # Password ke hash kore save kora
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email'),
#             password=validated_data['password'],
#             role=validated_data.get('role', 'viewer') # Default role 'viewer'
#         )
#         return user

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'role']


# from rest_framework import serializers
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only = True, required = True, style = {"input_type" : "password"})

#     class Meta:
#         model = User
#         fields = ["first_name", "last_name", "username", "email", "password", "role"]

#         def create(self, validate_data):
#             user = User.objects.create_user(
#                 username= validate_data['username'],
#                 email = validate_data['email'],
#                 password=validate_data['password'],
#                 role = validate_data.get['role', 'viewer']
#             )
#             return user
        
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["username", "email", "role"]



from rest_framework import serializers
from django.contrib.auth import get_user_model

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


