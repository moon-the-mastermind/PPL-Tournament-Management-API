from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Match, TournamentStanding


@receiver(pre_save, sender=Match)
def store_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Match.objects.get(pk = instance.pk)
            instance.old_status = old.status
        except Match.DoesNotExist:
            instance.old_status = None
        
        else:
            instance.old_status = None


@receiver(post_save, sender=Match)
def update_standings(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)

    if old_status == "finished" or instance.status != "finished":
        return
    if not instance.winner:
        return
    
    tournament = instance.tournament
    team1 = instance.team1
    team2 = instance.team2
    winner = instance.winner
    loser = team2 if winner == team1 else team1

    winner_standing, _ = TournamentStanding.objects.get_or_create(
        tournament = tournament,
        team = winner
    )
    loser_standing, _ = TournamentStanding.objects.get_or_create(
        tournament = tournament,
        team = loser
    )

   #match_played update 
    winner_standing.match_played += 1
    loser_standing.match_played += 1

    #winner/lose update 
    winner_standing.won += 1
    winner_standing.points += 2

    loser_standing.lost += 1

    winner_standing.save()
    loser_standing.save()
    
