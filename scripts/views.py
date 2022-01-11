import json as js
import os
from tempfile import TemporaryFile

# Create your views here.
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.views import generic
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from scripts import filters, forms, models, script_json, tables, characters
from collections import Counter


class ScriptsListView(SingleTableMixin, FilterView):
    model = models.ScriptVersion
    table_class = tables.ScriptTable
    template_name = "index.html"
    filterset_class = filters.ScriptVersionFilter

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(ScriptsListView, self).get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs

    table_pagination = {"per_page": 20}
    ordering = ["-pk"]


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

    def get_initial(self):
        initial = super().get_initial()
        script_pk = self.request.GET.get("script", None)
        if script_pk:
            script = models.Script.objects.get(pk=script_pk)
            if script:
                script_version = script.latest_version()
                initial["name"] = script.name
                initial["author"] = script_version.author
                initial["version"] = script_version.version
                if script_version.notes:
                    initial["notes"] = script_version.notes
        return initial

    def get_form_kwargs(self):
        """
        We want to provide the user to the Form's clean method so the user
        can't overwrite scripts owned by someone else.
        """
        kwargs = super(ScriptUploadView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_form(self):
        """
        If this is an anonymous user, don't allow them to add notes.
        """
        form = super().get_form(self.form_class)

        # If this user isn't authenticated, do allow them to add notes.
        # Otherwise, if this not a new script and this user does not own the existing
        # script, don't allow them to add notes.
        if not self.request.user.is_authenticated:
            form.fields.pop("notes")
        else:
            script_pk = self.request.GET.get("script", None)
            if script_pk:
                script = models.Script.objects.get(pk=script_pk)
                if script and script.owner and (script.owner != self.request.user):
                    form.fields.pop("notes")

        return form

    def get_success_url(self):
        return "/script/" + str(self.script_version.script.pk)

    def form_valid(self, form):
        user = self.request.user
        json = forms.get_json_content(form.cleaned_data)

        # Use the script name from the JSON in preference of the text field.
        script_name = script_json.get_name_from_json(json)
        if not script_name:
            script_name = form.cleaned_data["name"]

        # Either get the current script, or create a new one based on the name.
        script, created = models.Script.objects.get_or_create(name=script_name)

        # We only want to set the owner on newly created scripts, so if we've
        # just created the script and the user is authenticated, set the owner to this user.
        if created and user.is_authenticated:
            script.owner = user
            script.save()

        # If we're updating an existing script, remove the latest tag from the current
        # latest script version.
        if script.versions.count() > 0:
            latest = script.latest_version()
            latest.latest = False
            latest.save()

        # Use the author in the JSON in preference of the text field.
        author = script_json.get_author_from_json(json)
        if not author:
            author = form.cleaned_data["author"]

        # Create the Script Version object from the form.
        self.script_version = models.ScriptVersion.objects.create(
            version=form.cleaned_data["version"],
            script_type=form.cleaned_data["script_type"],
            content=json,
            script=script,
            pdf=form.cleaned_data["pdf"],
            author=author,
        )
        self.script_version.tags.set(form.cleaned_data["tags"])
        return super().form_valid(form)


class StatisticsView(generic.TemplateView):
    template_name = "statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = models.Script.objects.count()

        character_count = {}
        for type in characters.CharacterType:
            character_count[type.value] = Counter()
        for character in characters.Character:
            character_count[character.character_type.value][
                character.character_name
            ] = models.ScriptVersion.objects.filter(
                latest=True, content__contains=[{"id": character.json_id}]
            ).count()

        for type in characters.CharacterType:
            context[type.value] = character_count[type.value].most_common(5)
            context[type.value + "least"] = character_count[type.value].most_common()[
                :-6:-1
            ]

        return context


class UserEditView(generic.edit.UpdateView):
    """Allow view and update of basic user data.
    In practice this view edits a model, and that model is
    the User object itself, specifically the names that
    a user has.
    The key to updating an existing model, as compared to creating
    a model (i.e. adding a new row to a database) by using the
    Django generic view ``UpdateView``, specifically the
    ``get_object`` method.
    """

    form_class = forms.UserEditForm
    template_name = "account/profile.html"
    success_url = "/accounts/profile"

    def get_object(self):
        return self.request.user


def vote_for_script(request, pk: int):
    if request.method != "POST":
        raise Http404()
    script_version = models.ScriptVersion.objects.get(pk=pk)

    # Authenticated users should create votes with their user profile.
    if request.user.is_authenticated:
        if models.Vote.objects.filter(
            user=request.user, script=script_version
        ).exists():
            # If this user has already voted for this script, delete that vote. Use filter.exists()
            # because it is more performant
            vote = models.Vote.objects.get(user=request.user, script=script_version)
            vote.delete()
        else:
            # Otherwise create a new vote.
            models.Vote.objects.create(user=request.user, script=script_version)
    elif not request.session.get(str(pk), False):
        # Non-authenticated users have to track scripts we've voted for with session state.
        models.Vote.objects.create(script=script_version)
        request.session[str(pk)] = True
    return redirect(request.POST["next"])


def download_json(request, pk: int, version: str) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    json_content = js.JSONEncoder().encode(script_version.content)
    temp_file = TemporaryFile()
    temp_file.write(json_content.encode("utf-8"))
    temp_file.flush()
    temp_file.seek(0)
    response = FileResponse(
        temp_file, as_attachment=True, filename=(script.name + ".json")
    )
    return response


def download_pdf(request, pk: int, version: str) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    if os.environ.get("DJANGO_HOST", None):
        return FileResponse(script_version.pdf, as_attachment=True)
    else:
        return FileResponse(open(script_version.pdf.name, "rb"), as_attachment=True)
