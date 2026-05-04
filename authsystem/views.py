from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model
from . serializers import RegistrationSerializer, UserSerializer, ProfileSerializer
from django.shortcuts import get_object_or_404
from .models import PlayerProfile


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

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        # get object request.user k extract korche ebong prottek ta user k return kortese
        return get_object_or_404(PlayerProfile, user=self.request.user)

    