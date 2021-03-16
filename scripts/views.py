from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, FileResponse
from django.views import generic
from . import models
from tempfile import TemporaryFile
import os
import json

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
            context['script_version'] = self.object.versions.last()
        return context

def download_script(self, pk, version):
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    json_content = json.JSONEncoder().encode(script_version.content)
    temp_file = TemporaryFile()
    temp_file.write(json_content.encode('utf-8'))
    temp_file.flush()
    temp_file.seek(0)
    response = FileResponse(temp_file, as_attachment=True, filename=(script.name + '.json'))
    return response
