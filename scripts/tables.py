import django_tables2 as tables

from scripts.models import ScriptVersion

table_class = {
    "td": {"class": "pl-2 p-0 pr-2 align-middle text-center"},
    "th": {"class": "align-middle text-center"},
}
button_table_class = {
    "td": {"class": "pl-2 p-0 pr-2 align-middle text-center", "style": "width:1%"},
    "th": {"class": "align-middle text-center", "style": "width:1%"},
}
favourite_table_class = {
    "td": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:1%"},
    "th": {"class": "align-middle text-center", "style": "width:1%"},
}


class ScriptTable(tables.Table):
    class Meta:
        model = ScriptVersion
        exclude = ("id", "content", "script", "latest", "created", "notes")
        sequence = (
            "name",
            "version",
            "author",
            "script_type",
            "score",
            "tags",
            "json",
            "pdf",
        )
        orderable = True

    name = tables.Column(
        empty_values=(),
        order_by="script.name",
        linkify=(
            "script",
            {"pk": tables.A("script.pk"), "version": tables.A("version")},
        ),
        attrs={"td": {"class": "pl-1 p-0 pr-2 align-middle"}},
    )
    script_type = tables.Column(attrs=table_class, verbose_name="Type")
    author = tables.Column(attrs=table_class)
    version = tables.Column(attrs=table_class)
    json = tables.TemplateColumn(
        orderable=False, template_name="download_json.html", attrs=button_table_class
    )
    pdf = tables.TemplateColumn(
        orderable=False, template_name="download_pdf.html", attrs=button_table_class
    )
    score = tables.Column(attrs=table_class, order_by="-score")
    tags = tables.TemplateColumn(
        orderable=False, template_name="tags.html", attrs=table_class
    )

    def render_name(self, value, record):
        return record.script.name

    def render_type(self, value, record):
        return record.type


class UserScriptTable(ScriptTable):
    class Meta:
        model = ScriptVersion
        exclude = ("id", "content", "script", "latest", "created", "notes")
        sequence = (
            "name",
            "version",
            "author",
            "script_type",
            "score",
            "tags",
            "json",
            "pdf",
            "vote",
            "favourite",
        )
        orderable = True

    vote = tables.TemplateColumn(
        orderable=False, template_name="vote.html", attrs=button_table_class
    )
    favourite = tables.TemplateColumn(
        orderable=False, template_name="favourite.html", attrs=favourite_table_class
    )
