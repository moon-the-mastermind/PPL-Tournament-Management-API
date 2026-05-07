from rest_framework import serializers
from .models import Team, TeamMember, Invitation
from authsystem.models import UserProfile


class TeamMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source="player.full_name")
    ssc_batch = serializers.ReadOnlyField(source="player.ssc_batch")
    username = serializers.ReadOnlyField(source="player.user.username")
    team = serializers.ReadOnlyField(source = 'team.name')
    class Meta:
        model = TeamMember
        fields = [
            "id", "username", "full_name", "ssc_batch", "team",
            "role", "jersey_number", "batting_style", "bowling_style"
        ]


class InvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source = 'team.name')
    is_valid = serializers.BooleanField(read_only = True)

    class Meta:
        model = Invitation
        fields = [
            "id", "team", "team_name", "token", "usage_limit", "used_count", "is_active", "is_valid", "created_at"
        ]
        read_only_fields = ["token", "used_count", "created_at"]

    def validate(self, data):
        team = data['team']
        user = self.context['request'].user
        
        if team.captain != user:
            raise serializers.ValidationError("You are not authorized to create invitations for this team.")
        
        # check if the team already have invite token 
        if Invitation.objects.filter(team=team, is_active=True).exists():
            raise serializers.ValidationError(
                "This team already has an active invitation. Deactivate the old one to create a new one."
            )   
        return data
    def create(self, validated_data):
        team = validated_data['team']
        # পুরনো সব ইনভিটেশন ডিঅ্যাক্টিভেট করে দেওয়া
        Invitation.objects.filter(team=team).update(is_active=False)
        return super().create(validated_data)

class TeamJoinSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=TeamMember.ROLE_CHOICES, default='batsman')

    def validate(self, data):
        user = self.context['request'].user
        profile = user.profile

        # ১. চেক করা প্লেয়ার অলরেডি কোনো টিমে আছে কি না (যেহেতু OneToOneField)
        if TeamMember.objects.filter(player=profile).exists():
            raise serializers.ValidationError("You are already a member of a team.")

        # ২. ইনভিটেশন টোকেন ভ্যালিডেশন
        try:
            invitation = Invitation.objects.get(token=data['token'], is_active=True)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive invitation token.")

        if not invitation.is_valid():
            raise serializers.ValidationError("Invitation limit reached or expired.")

        # ইনভিটেশন অবজেক্টটি পরবর্তী ব্যবহারের জন্য ডেটাতে সেভ করে রাখা
        data['invitation'] = invitation
        return data

class TeamSerializer(serializers.ModelSerializer):
    captain_name = serializers.ReadOnlyField(source="captain.profile.full_name")
    
    members = TeamMemberSerializer(source="team_members", many=True, read_only=True)
    
    active_invitations = InvitationSerializer(source="invitations", many=True, read_only=True)
    
    total_members = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id", "name", "captain", "captain_name", "logo", 
            "is_verified", "members", "total_members", 
            "active_invitations", "created_at"
        ]
        read_only_fields = ["is_verified", "captain", "id", "created_at"]

    def get_total_members(self, obj):
   
        return obj.team_members.count()


class TeamMemberDetailSerializer(serializers.ModelSerializer):
    # UserProfile থেকে পার্সোনাল তথ্য
    full_name = serializers.ReadOnlyField(source="player.full_name")
    ssc_batch = serializers.ReadOnlyField(source="player.ssc_batch")
    phone_number = serializers.ReadOnlyField(source="player.phone_number")
    image = serializers.ImageField(source="player.image", read_only=True)
    bio = serializers.ReadOnlyField(source="player.bio")
    
    # টিমের তথ্য
    team_name = serializers.ReadOnlyField(source="team.name")

    class Meta:
        model = TeamMember
        fields = [
            "id", "full_name", "ssc_batch", "phone_number", "image", "bio",
            "team_name", "role", "jersey_number", "batting_style", "bowling_style", 
            "created_at"
        ]