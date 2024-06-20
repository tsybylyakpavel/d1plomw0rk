# Административная панель
from django.contrib import admin
from .models import TournamentObject, Match, Team, Profile, Application,TeamMember

admin.site.register(TournamentObject)
admin.site.register(Match)
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Application)
admin.site.register(TeamMember)
