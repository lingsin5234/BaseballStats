from django.db import models

# CHOICES
WHICH_TEAM = [('away', 0), ('home', 1)]
PLAY_TYPE = [('play', 'play'), ('sub', 'sub')]


# Teams
class Team(models.Model):
    team_id = models.CharField(max_length=15)
    team_city = models.CharField(max_length=25)
    team_name = models.CharField(max_length=15)

    def __str__(self):
        return self.team_name


# Game Info
class GameInfo(models.Model):
    game_id = models.CharField(max_length=12)
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


# Game Plays
class GamePlay(models.Model):
    game_id = models.ForeignKey(GameInfo, null=True, on_delete=models.SET_NULL)
    inning = models.IntegerField()
    which_half = models.IntegerField(choices=WHICH_TEAM)
    half_inning = models.CharField(max_length=4)
    type_of_play = models.CharField(max_length=4, choices=PLAY_TYPE)
    which_team = models.IntegerField(choices=WHICH_TEAM)
    player_id = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_player'))
    pitcher_id = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_pitcher')
    the_play = models.CharField(max_length=40)
    1b_before = models.CharField(max_length=12)
    2b_before = models.CharField(max_length=12)
    3b_before = models.CharField(max_length=12)
    1b_after = models.CharField(max_length=12)
    2b_after = models.CharField(max_length=12)
    3b_after = models.CharField(max_length=12)
    runs_scored = models.IntegerField()
    outs = models.IntegerField()
    batting_spot = models.IntegerField()
    fielding_pos = models.IntegerField()

    def __str__(self):
        return self.game_id + ': ' + self.half_inning + ' - ' + self.the_play
