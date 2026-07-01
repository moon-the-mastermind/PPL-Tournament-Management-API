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
        total_overs = cleaned_data.get('total_overs')
        max_wickets = cleaned_data.get('max_wickets')

        # team1 and team2 cannot be the same
        if team1 and team2 and team1 == team2:
            self.add_error('team2', 'team1 and team2 cannot be the same.')

        # toss_winner must be one of the match teams
        if toss_winner and team1 and team2:
            if toss_winner not in [team1, team2]:
                self.add_error('toss_winner', 'Toss winner must be one of the match teams.')

        # batting_first must be one of the match teams
        if batting_first and team1 and team2:
            if batting_first not in [team1, team2]:
                self.add_error('batting_first', 'Batting first must be one of the match teams.')

        # winner must be one of the match teams
        if winner and team1 and team2:
            if winner not in [team1, team2]:
                self.add_error('winner', 'Winner must be one of the match teams.')

        # winner can only be set when match is finished
        if winner and status != 'finished':
            self.add_error('winner', 'Cannot set winner before the match is finished.')

        # winner is required when match is finished
        if status == 'finished' and not winner:
            self.add_error('winner', 'Winner is required to finish the match.')

        # total_overs validation
        if total_overs and total_overs < 1:
            self.add_error('total_overs', 'Total overs must be at least 1.')

        # max_wickets validation
        if max_wickets and max_wickets < 1:
            self.add_error('max_wickets', 'Max wickets must be at least 1.')

        if max_wickets and max_wickets > 10:
            self.add_error('max_wickets', 'Max wickets cannot be more than 10.')

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
    
    list_display = ('__str__', 'status', 'match_date', 'venue', 'winner', 'total_overs', 'max_wickets')
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