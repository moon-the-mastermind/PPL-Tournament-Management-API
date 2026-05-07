from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns=[
    # path("login/", views.home),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name = "login"),
    path("token/refresh/", TokenRefreshView.as_view(), name = "token_refresh"),
    path("profile/me/", views.MyProfileView.as_view(), name = "profile"),
    path("profile/public/<int:id>/", views.PublicProfileView.as_view(), name = "public_profile"),

]