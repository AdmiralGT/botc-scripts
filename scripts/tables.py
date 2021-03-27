import django_tables2 as tables
from .models import Script, ScriptVersion


class ScriptTable(tables.Table):
    class Meta:
        model = ScriptVersion
        exclude = ("id", "content", "script", "latest")
        sequence = ("name", "type", "version", "author", "score", "json", "pdf", "vote")

    name = tables.Column(
        empty_values=(),
        order_by="script.name",
        linkify=(
            "script",
            {"pk": tables.A("script.pk"), "version": tables.A("version")},
        ),
    )
    author = tables.Column()
    version = tables.Column()
    json = tables.TemplateColumn(
        orderable=False,
        template_name="download_json.html"
    )
    pdf = tables.TemplateColumn(
        orderable=False,
        template_name="download_pdf.html"
    )
    score = tables.Column()
    vote = tables.TemplateColumn(orderable=False, template_name="vote.html")

    def render_name(self, value, record):
        return record.script.name

    def render_type(self, value, record):
        return record.type