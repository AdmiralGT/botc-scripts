from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, FileResponse
from django.views import generic
from . import models, forms
from tempfile import TemporaryFile
import os
import json as js


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
    script_version = None

    def validate_json(self, json_data):
        pass

    def get_success_url(self):
        return '/script/' + str(self.script_version.script.pk)

    def get_author(self, json):
        for item in json:
            if item.get("id", "") == "_meta":
                return item.get("author")
        return None


    def form_valid(self, form):
        json_content = form.cleaned_data["content"]
        json = js.loads(json_content.read().decode("utf-8"))
        script, created = models.Script.objects.get_or_create(
            name=form.cleaned_data["name"]
        )
        author = self.get_author(json)
        self.script_version = models.ScriptVersion.objects.create(
            version=form.cleaned_data["version"], type=form.cleaned_data["type"], content=json, script=script, pdf=form.cleaned_data["pdf"], author=author
        )
        return super().form_valid(form)


def download_json(self, pk: int, version: str) -> FileResponse:
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

def download_pdf(self, pk: int, version: str) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    return FileResponse(open(script_version.pdf.name, 'rb'), as_attachment=True)
