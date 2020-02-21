from django.db import models


# Teams
class Team(models.Model):
    team_id = models.CharField(max_length=15)
    team_city = models.CharField(max_length=25)
    team_name = models.CharField(max_length=15)

    def __str__(self):
        return self.team_name


# Game Info
class GameInfo(models.Model):
    game_id = models.IntegerField()
    home_team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL, related_name='_home_team')
    away_team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL, related_name='_away_team')
    game_info = models.CharField(max_length=100)

    def __str__(self):
        return self.game_id


# Players
class Player(models.Model):
    player_id = models.CharField(max_length=10)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=25)

    def __str__(self):
        return self.player_id


# Starters
class Starter(models.Model):
    game_id = models.ForeignKey(GameInfo, null=True, on_delete=models.SET_NULL)
    away_1 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_1')
    away_2 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_2')
    away_3 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_3')
    away_4 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_4')
    away_5 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_5')
    away_6 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_6')
    away_7 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_7')
    away_8 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_8')
    away_9 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_9')
    away_10 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_away_10')
    home_1 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_1')
    home_2 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_2')
    home_3 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_3')
    home_4 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_4')
    home_5 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_5')
    home_6 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_6')
    home_7 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_7')
    home_8 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_8')
    home_9 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_9')
    home_10 = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_home_10')

    def __str__(self):
        return self.game_id
