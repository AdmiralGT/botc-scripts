from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from scripts import models, tables, views
from homebrew import filters

class ScriptsListView(SingleTableMixin, FilterView):
    model = models.ScriptVersion
    template_name = "scriptlist.html"
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]
    script_view = None

    def get_filterset_class(self):
        if self.request.user.is_authenticated:
            return filters.FavouriteHomebrewVersionFilter
        return filters.HomebrewVersionFilter

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(ScriptsListView, self).get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs

    def get_table_class(self):
        if self.request.user.is_authenticated:
            return tables.UserScriptTable
        return tables.ScriptTable

class HomebrewScriptView(views.ScriptView):
    template_name = "homebrew/script.html"

class HomebrewDeleteView(views.ScriptDeleteView):
    def determine_success_url(self, script):
        return f"/homebrew/script/{script.pk}"

