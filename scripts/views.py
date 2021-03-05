from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import generic
from . import models

class ScriptsView(generic.ListView):
    template_name = "index.html"
    model = models.Script

class ScriptView(generic.DetailView):
    template_name = "script.html"
    model = models.Script

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "sel_name" in self.request.GET:
            context['script_version'] = self.object.versions.get(version=self.request.GET["sel_name"])
        else:
            context['script_version'] = self.object.versions.latest('pk')
        return context