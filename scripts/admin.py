from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Script, ScriptVersion, Vote

admin.site.register(Script)
admin.site.register(ScriptVersion)
admin.site.register(Vote)
