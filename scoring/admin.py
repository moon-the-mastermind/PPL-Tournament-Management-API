from django.contrib import admin
from .models import Ball, MatchState, BattingStats, BowlingStats


@admin.register(Ball)
class BallAdmin(admin.ModelAdmin):
    list_display = ('match', 'innings', 'over', 'ball_num', 'batsman', 'bowler', 'runs', 'is_wicket')
    list_filter = ('match', 'innings', 'is_wicket')
    ordering = ['match', 'innings', 'over', 'ball_num']


@admin.register(MatchState)
class MatchStateAdmin(admin.ModelAdmin):
    list_display = ('match', 'current_innings', 'striker', 'non_striker', 'current_bowler', 'total_runs', 'total_wickets', 'total_balls', 'is_active')
    list_filter = ('current_innings', 'is_active')


@admin.register(BattingStats)
class BattingStatsAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'team', 'runs', 'balls', 'fours', 'sixes', 'is_out')
    list_filter = ('match', 'team', 'is_out')


@admin.register(BowlingStats)
class BowlingStatsAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'team', 'overs', 'runs_conceded', 'wickets')
    list_filter = ('match', 'team')