import django_filters
from .models import ScriptVersion

class ScriptVersionFilter(django_filters.FilterSet):
    class Meta:
        model = ScriptVersion
        fields = ['type']