from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.shortcuts import get_object_or_404
from .models import Team, TeamMember, Invitation
from .serializers import(

            InvitationSerializer, TeamSerializer, 
            TeamMemberSerializer, TeamMemberDetailSerializer,
            TeamJoinSerializer,
            
        ) 
from django_filters.rest_framework import DjangoFilterBackend


# team update er jonne captain k permission set
class IsTeamCaptain(permissions.BasePermission):
    #only captain can edit
    def has_object_permission(self, request, view, obj):
        return obj.captain == request.user


class TeamDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamCaptain]
    lookup_field = "id"


class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_verified']

class TeamDetailView(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

class GenerateInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)

        if team.captain != request.user:
            return Response({"error": "Only captain can generate the invitation."}, status=status.HTTP_403_FORBIDDEN)
        
        invitation, created = Invitation.objects.get_or_create(team=team)

        if not invitation.is_active:
            invitation.is_active = True
            invitation.save()

        serializer = InvitationSerializer(invitation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class JoinTeamView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TeamJoinSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            invitation = serializer.validated_data['invitation']
            role = serializer.validated_data['role']
            profile = request.user.profile

            TeamMember.objects.create(
                team=invitation.team, 
                player=profile, 
                role=role
            )

            invitation.used_count += 1
            invitation.save()

            return Response({
                "message": f"Congratulations! You successfully joined {invitation.team.name}"
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TeamMemberListView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'team__name': ['iexact', 'icontains'],
        'role': ['exact'],
        'player__ssc_batch': ['exact', 'icontains'],
    }

    def get_queryset(self):
        return TeamMember.objects.select_related('player', 'player__user', 'team').filter(is_active=True)
    

class TeamMemberDetailView(generics.RetrieveAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 
