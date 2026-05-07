from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model
from . serializers import RegistrationSerializer, UserSerializer, PublicProfileSerializer, PrivateProfileSerializer
from django.shortcuts import get_object_or_404
from .models import UserProfile


def home(request):
    return render(request, 'home.html')

class RegisterView(generics.CreateAPIView):
    User = get_user_model()
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user" : UserSerializer(user).data,
                    "refresh" : str(refresh),
                    "access" : str(refresh.access_token),
                    "message" : "User Registered Successfully",
                }, status= status.HTTP_201_CREATED
     
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PrivateProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class PublicProfileView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = PublicProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

