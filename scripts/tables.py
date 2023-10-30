import django_tables2 as tables

from scripts.models import ScriptVersion, Collection

table_class = {
    "td": {"class": "p-2 align-middle text-center"},
    "th": {"class": "align-middle text-center"},
}

script_table_actions_class = {
    "td": {"class": "p-2 align-middle text-center" },
    "th": {"class": "align-middle text-center"},
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
    "version",
    "pdf"
)


class ScriptTable(tables.Table):
    class Meta:
        model = ScriptVersion
        exclude = excluded_script_version_fields
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

    name = tables.Column(
        empty_values=(),
        order_by= ( "script.name", "-version" ),
        linkify=(
            "script",
            {"pk": tables.A("script.pk"), "version": tables.A("version")},
        ),
        attrs={"td": {"class": "p-2 align-middle"}},
    )
    
    author = tables.Column(attrs=table_class)
    
    script_type = tables.Column(attrs=table_class, verbose_name="Type")
    
    score = tables.TemplateColumn(
        attrs = table_class, 
        template_name = "script_table/likes.html", 
        verbose_name = "Likes",
        order_by = ("-score")
    )
    
    num_favs = tables.TemplateColumn(
        attrs = table_class, 
        template_name = "script_table/favourites.html", 
        verbose_name = "Favourites",
        order_by = ("-num_favs")
    )
    
    tags = tables.TemplateColumn(
        orderable = False, 
        template_name = "tags.html", 
        attrs = { 
            "td": {"class": "p-2 align-middle text-center" },
            "th": {"class": "p-2 align-middle text-center w-25"}
        },
    )
    
    actions = tables.TemplateColumn(
        template_name = "script_table/actions/default.html",
        orderable = False,
        verbose_name = "",
        attrs = script_table_actions_class,
    )

    def render_name(self, value, record):
        return "{name} ({version})".format(name=record.script.name, version=record.version)


class UserScriptTable(ScriptTable):
    class Meta:
        model = ScriptVersion
        exclude = excluded_script_version_fields
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
        
    actions = tables.TemplateColumn(
        template_name = "script_table/actions/authenticated.html",
        orderable = False,
        verbose_name = "",
        attrs = script_table_actions_class,
    )


class CollectionScriptTable(UserScriptTable):
    class Meta:
        model = ScriptVersion
        exclude = excluded_script_version_fields
        sequence = (
            "name",
            "author",
            "script_type",
            "score",
            "num_favs",
            "tags",
            "actions",
        )

    actions = tables.TemplateColumn(
        template_name = "script_table/actions/collection.html",
        orderable=False,
        verbose_name="",
        attrs = script_table_actions_class,
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
