import django_tables2 as tables

from scripts.models import ScriptVersion, Collection

table_class = {
    "td": {"class": "pl-2 pr-2 p-0 align-middle text-center"},
    "th": {"class": "align-middle text-center"},
}

# Ensure that the buttons only ever take up one line
script_table_actions_class = {
    "td": {"class": "pl-2 pr-2 p-0 align-middle text-center", "style": "width:15%"},
    "th": {"class": "align-middle text-center", "style": "width:15%"},
}

script_table_class = {
    "td": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:10%"},
    "th": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:10%"},
}

excluded_clocktower_version_fields = (
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
    "homebrewiness",
)


class ScriptTable(tables.Table):
    name = tables.Column(
        empty_values=(),
        order_by=("script.name", "-version"),
        linkify=(
            "script",
            {"pk": tables.A("script.pk"), "version": tables.A("version")},
        ),
        attrs={"td": {"class": "pl-2 pr-2 p-0 align-middle"}},
    )

    author = tables.Column(attrs=table_class)

    script_type = tables.Column(attrs=table_class, verbose_name="Type")

    score = tables.TemplateColumn(
        template_name="script_table/likes.html",
        verbose_name="Likes",
        order_by=("-score"),
        attrs={
            "td": {"class": "pl-2 pr-2 p-0 align-middle text-center"},
            "th": {"class": "align-middle text-center"},
        },
    )

    num_favs = tables.TemplateColumn(
        template_name="script_table/favourites.html",
        verbose_name="Favs",
        order_by=("-num_favs"),
        attrs={
            "td": {"class": "pl-2 pr-2 p-0 align-middle text-center"},
            "th": {"class": "align-middle text-center"},
        },
    )

    actions = tables.TemplateColumn(
        template_name="script_table/actions/default.html",
        orderable=False,
        verbose_name="",
        attrs=script_table_actions_class,
    )

    def render_name(self, value, record):
        return "{name} ({version})".format(name=record.script.name, version=record.version)


class ClocktowerTable(ScriptTable):
    tags = tables.TemplateColumn(
        orderable=False,
        template_name="tags.html",
        attrs={
            "td": {"class": "pl-2 pr-2 p-0 align-middle text-center"},
            "th": {"class": "pl-2 pr-2 p-0 align-middle text-center"},
        },
    )

    class Meta:
        model = ScriptVersion
        exclude = excluded_clocktower_version_fields
        sequence = (
            "name",
            "author",
            "script_type",
            "score",
            "num_favs",
            "tags",
            "actions",
        )
        orderable = True


class UserClocktowerTable(ClocktowerTable):
    actions = tables.TemplateColumn(
        template_name="script_table/actions/authenticated.html",
        orderable=False,
        verbose_name="",
        attrs=script_table_actions_class,
    )

    class Meta:
        model = ScriptVersion
        exclude = excluded_clocktower_version_fields
        sequence = (
            "name",
            "author",
            "script_type",
            "score",
            "num_favs",
            "tags",
            "actions",
        )
        orderable = True


class CollectionClocktowerTable(UserClocktowerTable):
    actions = tables.TemplateColumn(
        template_name="script_table/actions/collection.html",
        orderable=False,
        verbose_name="",
        attrs=script_table_actions_class,
    )

    class Meta:
        model = ScriptVersion
        exclude = excluded_clocktower_version_fields
        sequence = (
            "name",
            "author",
            "script_type",
            "score",
            "num_favs",
            "tags",
            "actions",
        )
        orderable = True


class CollectionTable(tables.Table):
    name = tables.Column(
        empty_values=(),
        linkify=(
            "collection",
            {"pk": tables.A("pk")},
        ),
        attrs={"td": {"class": "pl-1 p-0 pr-2 align-middle"}},
    )
    description = tables.Column(attrs=table_class)
    scripts_in_collection = tables.Column(
        attrs=script_table_class,
        verbose_name="Scripts",
        order_by="-scripts_in_collection",
    )

    class Meta:
        model = Collection
        exclude = ("id", "owner", "scripts", "notes")
        sequence = (
            "name",
            "description",
            "scripts_in_collection",
        )
        orderable = True
