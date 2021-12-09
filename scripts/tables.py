import django_tables2 as tables

from .models import Script, ScriptVersion
from .characters import Character

table_class = {"td": {"class": "pl-2 p-0 pr-2 align-middle text-center"}}


class ScriptTable(tables.Table):
    class Meta:
        model = ScriptVersion
        exclude = ("id", "content", "script", "latest", "created")
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
        orderable=False, template_name="download_json.html", attrs=table_class
    )
    pdf = tables.TemplateColumn(
        orderable=False, template_name="download_pdf.html", attrs=table_class
    )
    score = tables.Column(attrs=table_class)
    vote = tables.TemplateColumn(
        orderable=False, template_name="vote.html", attrs=table_class
    )
    tags = tables.TemplateColumn(
        orderable=False, template_name="tags.html", attrs=table_class
    )

    def render_name(self, value, record):
        return record.script.name

    def render_type(self, value, record):
        return record.type


def generate_stats_data():
    data = {}
    for character in Character:
        data[character.character_name] = get_number_of_characters_in_database(character)


class StatsTable(tables.Table):
    name = tables.Column()
    type = tables.Column()
    count = tables.Column()


def get_number_of_characters_in_database(character):
    return (
        ScriptVersion.objects.all()
        .filter(content__contains=[{"id": character.json_id}])
        .count()
    )
