import django_tables2 as tables

from scripts.models import ScriptVersion, Collection

table_class = {
    "td": {"class": "pl-2 p-0 pr-2 align-middle text-center"},
    "th": {"class": "align-middle text-center"},
}
button_table_class = {
    "td": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:1%"},
    "th": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:1%"},
}
favourite_table_class = {
    "td": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:1%"},
    "th": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:1%"},
}
script_table_class = {
    "td": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:10%"},
    "th": {"class": "pl-1 p-0 pr-1 align-middle text-center", "style": "width:10%"},
}

excluded_script_version_fields = (
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
)


class ScriptTable(tables.Table):
    class Meta:
        model = ScriptVersion
        exclude = excluded_script_version_fields
        sequence = (
            "name",
            "version",
            "author",
            "script_type",
            "info",
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
    info = tables.TemplateColumn(
        template_name="info.html",
        attrs=script_table_class,
        order_by=("-score", "-num_favs", "-num_comments"),
    )
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
        exclude = excluded_script_version_fields
        sequence = (
            "name",
            "version",
            "author",
            "script_type",
            "info",
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


class CollectionScriptTable(UserScriptTable):
    class Meta:
        model = ScriptVersion
        exclude = excluded_script_version_fields
        sequence = (
            "name",
            "version",
            "author",
            "script_type",
            "info",
            "tags",
            "json",
            "pdf",
            "vote",
            "favourite",
            "remove_from_collection",
        )

    remove_from_collection = tables.TemplateColumn(
        orderable=False,
        template_name="remove_collection.html",
        attrs=button_table_class,
        verbose_name="Remove",
    )


class CollectionTable(tables.Table):
    class Meta:
        model = Collection
        exclude = ("id", "owner", "scripts", "notes")
        sequence = (
            "name",
            "description",
            "scripts_in_collection",
        )
        orderable = True

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
