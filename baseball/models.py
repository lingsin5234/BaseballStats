from django.db import models
from .oper import date_time as dt

# CHOICES
WHICH_TEAM = [('away', 0), ('home', 1)]
PLAY_TYPE = [('play', 'play'), ('sub', 'sub')]
STAT_CATEGORY = [('batting', 0), ('pitching', 1), ('defense', 2)]

# constants
YEARS = dt.gen_year()
TEAMS = (('ANA', 'ANA'), ('ARI', 'ARI'), ('ATL', 'ATL'), ('BAL', 'BAL'), ('BOS', 'BOS'), ('CHA', 'CHA'),
         ('CHN', 'CHN'), ('CIN', 'CIN'), ('CLE', 'CLE'), ('COL', 'COL'), ('DET', 'DET'), ('HOU', 'HOU'),
         ('KCA', 'KCA'), ('LAN', 'LAN'), ('MIA', 'MIA'), ('MIL', 'MIL'), ('MIN', 'MIN'), ('NYA', 'NYA'),
         ('NYN', 'NYN'), ('OAK', 'OAK'), ('PHI', 'PHI'), ('PIT', 'PIT'), ('SDN', 'SDN'), ('SEA', 'SEA'),
         ('SFN', 'SFN'), ('SLN', 'SLN'), ('TBA', 'TBA'), ('TEX', 'TEX'), ('TOR', 'TOR'), ('WAS', 'WAS'))
FORM_TYPE = (('import_year', 'import_year'), ('process_team', 'process_team'), ('generate_stats', 'generate_stats'),
             ('view_stats', 'view_stats'))


# Extract/Process Requests
class JobRequirements(models.Model):
    year = models.IntegerField(choices=YEARS)
    team = models.CharField(max_length=4, choices=TEAMS)
    form_type = models.CharField(max_length=20, choices=FORM_TYPE, null=True, default=None)

    def __str__(self):
        return str(self.year) + str(self.team) + str(self.form_type)


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
    type_of_play = models.CharField(max_length=4, choices=PLAY_TYPE)
    inning = models.IntegerField()
    which_half = models.IntegerField(choices=WHICH_TEAM)
    half_innings = models.CharField(max_length=4)
    player_id = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_player')
    pitch_count = models.CharField(max_length=2)
    pitches = models.CharField(max_length=30)
    the_play = models.CharField(max_length=40)
    # player_name -- does this need reference?
    which_team = models.IntegerField(choices=WHICH_TEAM)
    team_name = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL)
    batting_spot = models.IntegerField()
    fielding_pos = models.IntegerField()
    pitcher_id = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='_pitcher')
    num_of_outs = models.IntegerField()
    before_1b = models.CharField(max_length=12)
    before_2b = models.CharField(max_length=12)
    before_3b = models.CharField(max_length=12)
    after_1b = models.CharField(max_length=12)
    after_2b = models.CharField(max_length=12)
    after_3b = models.CharField(max_length=12)
    runs_scored = models.IntegerField()
    total_scored = models.IntegerField()

    def __str__(self):
        return self.game_id + ': ' + self.half_inning + ' - ' + self.the_play


# Stat Collector
class StatCollect(models.Model):
    player_id = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    team_name = models.CharField(max_length=3)
    game_id = models.ForeignKey(GameInfo, null=True, on_delete=models.SET_NULL)
    half_inning = models.CharField(max_length=4)
    stat_type = models.CharField(max_length=5)
    stat_value = models.IntegerField()
    actual_play = models.CharField(max_length=40)
    num_of_outs = models.IntegerField()
    bases_taken = models.CharField(max_length=3)
    stat_team = models.IntegerField(choices=WHICH_TEAM)
    stat_category = models.CharField(max_length=8, choices=STAT_CATEGORY)

    def __str__(self):
        return player_id + ' stat for ' + stat_type + ': ' + stat_value
