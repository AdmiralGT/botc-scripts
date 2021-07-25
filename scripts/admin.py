# Register your models here.
from django.contrib import admin
from .models import Script, ScriptTag, ScriptVersion, Vote

admin.site.register(Script)
admin.site.register(ScriptVersion)
admin.site.register(ScriptTag)
admin.site.register(Vote)
