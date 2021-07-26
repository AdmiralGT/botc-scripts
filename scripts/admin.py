# Register your models here.
from django.contrib import admin
from .models import Script, ScriptTag, ScriptVersion, Vote

class ScriptVersionAdmin(admin.ModelAdmin):
    readonly_fields=["created"]

admin.site.register(Script)
admin.site.register(ScriptVersion, ScriptVersionAdmin)
admin.site.register(ScriptTag)
admin.site.register(Vote)
