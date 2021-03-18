from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, FileResponse
from django.views import generic
from . import models, forms
from tempfile import TemporaryFile
from packaging.version import Version
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
            context["script_version"] = self.object.versions.get(
                version=self.request.GET["sel_name"]
            )
        else:
            context["script_version"] = self.object.versions.last()
        return context


class ScriptUploadView(generic.FormView):
    template_name = "upload.html"
    form_class = forms.ScriptForm

    def validate_json(self, json_data):
        pass

    def form_valid(self, form):
        json_content = form.cleaned_data["content"]
        json_blob = json_content.read().decode("utf-8")
        json_loaded = json.loads(json_blob)
        script, created = models.Script.objects.get_or_create(
            name=form.cleaned_data["name"]
        )
        if script.versions.count() == 0:
            models.ScriptVersion.objects.create(
                version=form.cleaned_data["version"], type=form.cleaned_data["type"], content=json_loaded, script=script
            )
        elif Version(form.cleaned_data["version"]) < Version(
            str(script.latest_version().version)
        ):
            print("Bad Version")
        else:
            models.ScriptVersion.objects.create(
                version=form.cleaned_data["version"], type=form.cleaned_data["type"], content=json_loaded, script=script
            )
        return HttpResponse()


def download_script(self, pk: int, version: str) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    json_content = json.JSONEncoder().encode(script_version.content)
    temp_file = TemporaryFile()
    temp_file.write(json_content.encode("utf-8"))
    temp_file.flush()
    temp_file.seek(0)
    response = FileResponse(
        temp_file, as_attachment=True, filename=(script.name + ".json")
    )
    return response
