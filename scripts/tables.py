import django_tables2 as tables
from .models import Script, ScriptVersion

class ScriptTable(tables.Table):
    class Meta:
        model = ScriptVersion
        exclude = ('id','content','script','latest')
        sequence = ('name', 'type', 'version', 'author', 'json', 'pdf')

    name = tables.Column(empty_values=(), order_by='script.name', linkify=("script", { "pk": tables.A("script.pk"), "version": tables.A("version")}))
    author = tables.Column()
    version = tables.Column()
    json = tables.Column(empty_values=(), orderable=False, linkify=("download_json", { "pk": tables.A("script.pk"), "version": tables.A("version")}))
    pdf = tables.Column(orderable=False, linkify=("download_pdf", { "pk": tables.A("script.pk"), "version": tables.A("version")}))

    def render_name(self, value, record):
        return record.script.name

    def render_type(self, value, record):
        return record.type

    def render_json(self, value, record):
        return "Download"
