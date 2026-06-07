from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Team, TeamMember
@receiver(post_save, sender=Team)
def manage_captain_membership(sender, created, instance, **kwargs):
    if instance.captain:
        try:
            captain_profile = instance.captain.profile
            existing_member = TeamMember.objects.filter(player= captain_profile).first()

            if existing_member:
                TeamMember.objects.filter(pk = existing_member.pk).update(team= instance)
            
            else:
                TeamMember.objects.create(
                    team = instance,
                    player = captain_profile
                )
        except Exception as e:
            print(f"CRITICAL ERROR in signals : {e}")


