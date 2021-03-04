from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Script, ScriptVersion

admin.site.register(Script)
admin.site.register(ScriptVersion)
