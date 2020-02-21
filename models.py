from django.db import models


# Teams
class Teams(models.Model):
    team_id = models.CharField(max_length=15)
    team_city = models.CharField(max_length=25)
    team_name = models.CharField(max_length=15)

    def __str__(self):
        return self.team_name


# Game Info
class GameInfo(models.Model):
    game_id = models.IntegerField()
    home_team = models.ForeignKey(Teams, null=True, on_delete=models.SET_NULL)
    away_team = models.ForeignKey(Teams, null=True, on_delete=models.SET_NULL)
    game_info = models.CharField(max_length=100)

    def __str__(self):
        return self.game_id


# Players
class Players(models.Model):
    player_id = models.CharField(max_length=10)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=25)

    def __str__(self):
        return self.player_id


# Starters
class Starters(models.Model):
    game_id = models.ForeignKey(GameInfo, null=True, on_delete=models.SET_NULL)
    away_1 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_2 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_3 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_4 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_5 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_6 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_7 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_8 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_9 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    away_10 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_1 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_2 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_3 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_4 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_5 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_6 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_7 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_8 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_9 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)
    home_10 = models.ForeignKey(Players, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.game_id
