import django_tables2 as tables
from .models import Script

class PersonTable(tables.Table):
    class Meta:
        model = Script
        template_name = "django_tables2/bootstrap4.html"
