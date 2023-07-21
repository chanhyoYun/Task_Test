from django.contrib import admin
from .models import *


class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "id"]


class SubTaskAdmin(admin.ModelAdmin):
    list_display = ["task", "id"]


admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)
