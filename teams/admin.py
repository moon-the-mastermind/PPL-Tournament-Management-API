from django.contrib import admin
from .models import Team, Invitation, TeamMember
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from django.db import transaction, IntegrityError
from django.contrib import messages

# admin.site.register(Team)
admin.site.register(Invitation)
admin.site.register(TeamMember)

User = get_user_model()

class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        captain = cleaned_data.get('captain')
        
        if captain:
            # ডাটাবেসে সেভ হওয়ার আগেই চেক করা হচ্ছে
            exists = Team.objects.filter(captain=captain).exclude(pk=self.instance.pk).exists()
            if exists:
                # এটি ফরমের ওপর লাল এরর দেখাবে এবং সেভ হওয়া থামিয়ে দিবে
                self.add_error('captain', f"এই ইউজার ({captain.username}) ইতিমধ্যে অন্য একটি টিমের ক্যাপ্টেন!")
        
        return cleaned_data

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm  # ফর্মটি অবশ্যই কানেক্টেড থাকতে হবে
    list_display = ('name', 'captain', 'is_verified', 'created_at')

    # save_model থেকে অতিরিক্ত try-except সরিয়ে ফেলো যাতে জ্যাঙ্গো নিজেই বুঝতে পারে কখন সেভ করতে হবে
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "captain":
            # শুধুমাত্র যারা আসলেই ডাটাবেসে থাকা টিমের ক্যাপ্টেন, তাদের আইডি বের করা
            busy_captains = Team.objects.filter(captain__isnull=False).values_list('captain_id', flat=True)
            
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                # এডিট করার সময় বর্তমান টিমের ক্যাপ্টেনকে ড্রপডাউনে রাখা
                current_team = Team.objects.filter(pk=obj_id).first()
                if current_team and current_team.captain:
                    busy_captains = list(busy_captains)
                    if current_team.captain_id in busy_captains:
                        busy_captains.remove(current_team.captain_id)
            
            kwargs["queryset"] = User.objects.exclude(id__in=busy_captains)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)