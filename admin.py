from django.contrib import admin
from .models import Team, GameInfo, Player, Starter, GamePlay

# Register your models here.
admin.site.register(Team)
admin.site.register(GameInfo)
admin.site.register(Player)
admin.site.register(Starter)
admin.site.register(GamePlay)
