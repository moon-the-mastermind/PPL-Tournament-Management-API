from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Match, TournamentStanding


@receiver(pre_save, sender=Match)
def store_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Match.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Match.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


def balls_to_overs(balls):
    if balls == 0:
        return 0.0
    return balls // 6 + (balls % 6) / 10


def calculate_nrr(runs_scored, balls_faced, runs_conceded, balls_bowled):
    if balls_faced == 0 or balls_bowled == 0:
        return 0.0
    batting_rr = runs_scored / (balls_faced / 6)
    bowling_rr = runs_conceded / (balls_bowled / 6)
    return round(batting_rr - bowling_rr, 3)


@receiver(post_save, sender=Match)
def update_standings(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_old_status', None)

    if old_status == 'finished' or instance.status != 'finished':
        return

    if not instance.winner:
        return

    tournament = instance.tournament
    team1 = instance.team1
    team2 = instance.team2
    winner = instance.winner
    loser = team2 if winner == team1 else team1

    # Get MatchState for RR data
    try:
        from scoring.models import MatchState
        match_state = MatchState.objects.get(match=instance)
    except MatchState.DoesNotExist:
        match_state = None

    # Get standings
    winner_standing, _ = TournamentStanding.objects.get_or_create(
        tournament=tournament,
        team=winner
    )
    loser_standing, _ = TournamentStanding.objects.get_or_create(
        tournament=tournament,
        team=loser
    )

    # matches_played update
    winner_standing.matches_played += 1
    loser_standing.matches_played += 1

    # winner/loser update
    winner_standing.won += 1
    winner_standing.points += 2
    loser_standing.lost += 1

    # NRR data update
    if match_state:
        # batting_first team এর runs/balls
        batting_first = instance.batting_first

        if batting_first == winner:
            # winner batting first
            winner_standing.runs_scored += match_state.innings1_runs
            winner_standing.balls_faced += match_state.innings1_balls
            winner_standing.runs_conceded += match_state.innings2_runs
            winner_standing.balls_bowled += match_state.innings2_balls

            loser_standing.runs_scored += match_state.innings2_runs
            loser_standing.balls_faced += match_state.innings2_balls
            loser_standing.runs_conceded += match_state.innings1_runs
            loser_standing.balls_bowled += match_state.innings1_balls
        else:
            # loser batting first
            loser_standing.runs_scored += match_state.innings1_runs
            loser_standing.balls_faced += match_state.innings1_balls
            loser_standing.runs_conceded += match_state.innings2_runs
            loser_standing.balls_bowled += match_state.innings2_balls

            winner_standing.runs_scored += match_state.innings2_runs
            winner_standing.balls_faced += match_state.innings2_balls
            winner_standing.runs_conceded += match_state.innings1_runs
            winner_standing.balls_bowled += match_state.innings1_balls

        # NRR calculate
        winner_standing.nrr = calculate_nrr(
            winner_standing.runs_scored,
            winner_standing.balls_faced,
            winner_standing.runs_conceded,
            winner_standing.balls_bowled
        )
        loser_standing.nrr = calculate_nrr(
            loser_standing.runs_scored,
            loser_standing.balls_faced,
            loser_standing.runs_conceded,
            loser_standing.balls_bowled
        )

    winner_standing.save()
    loser_standing.save()