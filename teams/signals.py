from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Team, TeamMember
@receiver(post_save, sender=Team)
def manage_captain_membership(sender, created, instance, **kwargs):
    if instance.captain:
        try:
            captain_profile = instance.captain.profile
            
            # চেক করা হচ্ছে সে ইতিমধ্যে কোনো টিমের মেম্বার কিনা
            existing_member = TeamMember.objects.filter(player=captain_profile).first()
            
            if existing_member:
                # যদি অলরেডি মেম্বার থাকে, তার টিম আপডেট করে দাও
                existing_member.team = instance
                existing_member.save()
            else:
                # না থাকলে নতুন তৈরি করো
                TeamMember.objects.create(
                    team=instance,
                    player=captain_profile
                )
        except Exception as e:
            # এটি টার্মিনালে প্রিন্ট করো দেখার জন্য কী এরর হচ্ছে
            print(f"CRITICAL Error in signal: {e}")