from django.contrib import admin
from .models import *


class TeamAdmin(admin.ModelAdmin):
    list_display = ["team_name", "id"]


admin.site.register(Team, TeamAdmin)
admin.site.register(User)
