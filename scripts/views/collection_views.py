"""
Collection-related views.
"""
import logging
from typing import Dict, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views import generic
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, SingleTableView

from scripts import models, forms, tables, filters

logger = logging.getLogger(__name__)


class CollectionScriptListView(SingleTableView):
    """View for displaying scripts in a collection."""
    
    model = models.ScriptVersion
    template_name = "collection.html"
    table_pagination = {"per_page": 20}
    ordering = ["pk"]

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add collection to context."""
        context = super().get_context_data(**kwargs)
        context["collection"] = get_object_or_404(
            models.Collection,
            pk=self.kwargs["pk"]
        )
        return context

    def get_table_class(self):
        """Get appropriate table based on ownership."""
        collection = get_object_or_404(models.Collection, pk=self.kwargs["pk"])
        
        if self.request.user == collection.owner:
            return tables.CollectionClocktowerTable
        elif self.request.user.is_authenticated:
            return tables.UserClocktowerTable
        return tables.ClocktowerTable

    def get_queryset(self):
        """Get scripts in the collection."""
        collection = get_object_or_404(models.Collection, pk=self.kwargs["pk"])
        return collection.scripts.order_by("pk")


class CollectionListView(SingleTableMixin, FilterView):
    """View for listing all collections."""
    
    model = models.Collection
    template_name = "collection_list.html"
    table_pagination = {"per_page": 20}
    ordering = ["pk"]
    table_class = tables.CollectionTable
    filterset_class = filters.CollectionFilter


class CollectionCreateView(LoginRequiredMixin, generic.CreateView):
    """View for creating a new collection."""
    
    template_name = "upload.html"
    form_class = forms.CollectionForm
    model = models.Collection

    def form_valid(self, form):
        """Set owner to current user."""
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Redirect to the created collection."""
        return f"/collection/{self.object.id}"


class CollectionEditView(LoginRequiredMixin, generic.UpdateView):
    """View for editing a collection."""
    
    template_name = "upload.html"
    form_class = forms.CollectionForm
    model = models.Collection

    def get(self, request, *args, **kwargs):
        """Ensure user owns the collection."""
        self.object = self.get_object()
        if self.object.owner != self.request.user:
            raise Http404("Cannot edit a collection you don't own.")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Ensure owner remains the current user."""
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Redirect to the edited collection."""
        return f"/collection/{self.object.id}"


class CollectionDeleteView(LoginRequiredMixin, generic.DeleteView):
    """View for deleting a collection."""
    
    model = models.Collection
    success_url = "/"

    def form_valid(self, form):
        """Check ownership before deletion."""
        self.object = self.get_object()
        if self.object.owner != self.request.user:
            raise Http404("Cannot delete a collection you don't own.")
        
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class AddScriptToCollectionView(LoginRequiredMixin, generic.View):
    """View for adding a script to a collection."""
    
    def post(self, request, *args, **kwargs):
        """Add script to collection."""
        collection_id = request.POST.get("collection")
        script_version_id = request.POST.get("script_version")
        
        if not collection_id or not script_version_id:
            raise Http404("Missing required parameters")
            
        collection = get_object_or_404(models.Collection, pk=collection_id)
        
        # Check if user owns the collection
        if collection.owner != request.user:
            raise Http404("Cannot modify a collection you don't own.")
            
        script_version = get_object_or_404(models.ScriptVersion, pk=script_version_id)
        collection.scripts.add(script_version)
        
        return HttpResponseRedirect(
            f"/script/{script_version.script.pk}/{script_version.version}"
        )


class RemoveScriptFromCollectionView(LoginRequiredMixin, generic.View):
    """View for removing a script from a collection."""
    
    def post(self, request, *args, **kwargs):
        """Remove script from collection."""
        collection = get_object_or_404(models.Collection, pk=kwargs["collection"])
        
        # Check ownership
        if collection.owner != self.request.user:
            raise Http404("Cannot edit a collection you don't own.")
            
        script = get_object_or_404(models.ScriptVersion, pk=kwargs["script"])
        collection.scripts.remove(script)
        
        return HttpResponseRedirect(f"/collection/{collection.pk}")
