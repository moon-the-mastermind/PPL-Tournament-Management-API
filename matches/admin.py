from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import Tournament, Match, PlayingXI, TournamentStanding


# ===============================================================
# Match Admin Form — validation এখানে
# ===============================================================

class MatchAdminForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get('team1')
        team2 = cleaned_data.get('team2')
        toss_winner = cleaned_data.get('toss_winner')
        batting_first = cleaned_data.get('batting_first')
        winner = cleaned_data.get('winner')
        status = cleaned_data.get('status')
        
 

    

        # team1 আর team2 একই হতে পারবে না
        if team1 and team2 and team1 == team2:
            self.add_error('team2', 'team1 আর team2 একই হতে পারবে না।')

        # toss_winner অবশ্যই match এর team হতে হবে
        if toss_winner and team1 and team2:
            if toss_winner not in [team1, team2]:
                self.add_error('toss_winner', 'Toss winner এই match এর team না।')

        # batting_first অবশ্যই match এর team হতে হবে
        if batting_first and team1 and team2:
            if batting_first not in [team1, team2]:
                self.add_error('batting_first', 'Batting first এই match এর team না।')

        # winner অবশ্যই match এর team হতে হবে
        if winner and team1 and team2:
            if winner not in [team1, team2]:
                self.add_error('winner', 'Winner এই match এর team না।')

        # finished status এ winner দিতেই হবে
        if status == 'finished' and not winner:
            self.add_error('winner', 'Match finished করতে winner দিতে হবে।')
        
        if winner and status != "finished":
            self.add_error("winner", "Can't set winner before finished the match.")

        return cleaned_data


class PlayingXIAdminForm(forms.ModelForm):
    class Meta:
        model = PlayingXI
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        match = cleaned_data.get('match')
        team = cleaned_data.get('team')
        player = cleaned_data.get('player')

        if match and team:
            # team অবশ্যই match এর অংশ হতে হবে
            if team not in [match.team1, match.team2]:
                self.add_error('team', 'এই team টি এই match এ নেই।')

        if match and team and player:
            # player অবশ্যই team এর member হতে হবে
            if not team.team_members.filter(player=player).exists():
                self.add_error('player', 'এই player টি এই team এর member না।')

            # 11 জনের বেশি হতে পারবে না
            existing_count = PlayingXI.objects.filter(
                match=match, team=team
            ).exclude(pk=self.instance.pk).count()

            if existing_count >= 11:
                self.add_error('player', 'একটা team সর্বোচ্চ 11 জন player দিতে পারবে।')

        return cleaned_data


# ===============================================================
# Admin Registration
# ===============================================================

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    form = MatchAdminForm
    
    list_display = ('__str__', 'status', 'match_date', 'venue', 'winner')
    list_filter = ('status', 'tournament')


@admin.register(PlayingXI)
class PlayingXIAdmin(admin.ModelAdmin):
    form = PlayingXIAdminForm
    list_display = ('player', 'team', 'match')
    list_filter = ('team', 'match')

@admin.register(TournamentStanding)
class TournamentStandingAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'team', 'match_played', 'won', 'lost', 'points', 'nrr')
    list_filter = ('tournament',)