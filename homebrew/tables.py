import django_tables2
from scripts import tables
from homebrew import models

# Ensure that the buttons only ever take up one line
script_table_actions_class = {
    "td": {"class": "pl-2 pr-2 p-0 align-middle text-center", "style": "width:15%"},
    "th": {"class": "align-middle text-center", "style": "width:15%"},
}

script_table_class = {
    "td": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:10%"},
    "th": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:10%"},
}

excluded_homebrew_version_fields = (
    "id",
    "content",
    "script",
    "latest",
    "created",
    "notes",
    "num_townsfolk",
    "num_outsiders",
    "num_minions",
    "num_demons",
    "num_travellers",
    "num_fabled",
    "edition",
    "version",
    "pdf",
)


class HomebrewTable(tables.ScriptTable):
    class Meta:
        model = models.HomebrewVersion
        exclude = excluded_homebrew_version_fields
        sequence = (
            "name",
            "author",
            "script_type",
            "score",
            "num_favs",
            "actions",
        )
        orderable = True

class UserHomebrewTable(HomebrewTable):
    actions = django_tables2.TemplateColumn(
        template_name="script_table/actions/authenticated.html",
        orderable=False,
        verbose_name="",
        attrs=script_table_actions_class,
    )
