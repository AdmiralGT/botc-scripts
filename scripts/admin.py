# Register your models here.
from django.contrib import admin

from scripts import models
from homebrew import models as h_models


class ScriptVersionAdmin(admin.ModelAdmin):
    readonly_fields = ["created"]


admin.site.register(models.Character)
admin.site.register(models.Translation)
admin.site.register(models.Comment)
admin.site.register(models.Collection)
admin.site.register(models.Favourite)
admin.site.register(models.Script)
admin.site.register(models.ScriptVersion, ScriptVersionAdmin)
admin.site.register(models.ScriptTag)
admin.site.register(models.Vote)
admin.site.register(models.WorldCup)

admin.site.register(h_models.HomebrewCharacter)
admin.site.register(h_models.HomebrewVersion)
