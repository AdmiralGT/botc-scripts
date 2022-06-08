# Register your models here.
from django.contrib import admin

from scripts import models


class ScriptVersionAdmin(admin.ModelAdmin):
    readonly_fields = ["created"]


admin.site.register(models.Comment)
admin.site.register(models.Collection)
admin.site.register(models.Favourite)
admin.site.register(models.Script)
admin.site.register(models.ScriptVersion, ScriptVersionAdmin)
admin.site.register(models.ScriptTag)
admin.site.register(models.Vote)
admin.site.register(models.WorldCup)
