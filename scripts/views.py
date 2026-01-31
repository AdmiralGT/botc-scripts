import json as js
import os
from tempfile import TemporaryFile

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required
from django.db.models import Case, When, Count, Prefetch, F
from django.http import (
    FileResponse,
    JsonResponse,
    Http404,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponse,
)
from django.shortcuts import redirect
from django.views import generic
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, SingleTableView
from versionfield import Version

from scripts import (
    cache,
    constants,
    filters,
    forms,
    models,
    script_json,
    tables,
)
from collections import Counter
from django.contrib.postgres.search import TrigramSimilarity
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import requests


class ScriptsListView(SingleTableMixin, FilterView):
    model = models.ScriptVersion
    template_name = "scriptlist.html"
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]
    script_view = None

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "tags",
                    queryset=models.ScriptTag.objects.all().order_by("order"),
                )
            )
        )

    def get_filterset_class(self):
        if self.request.user.is_authenticated:
            return filters.FavouriteScriptVersionFilter
        return filters.ScriptVersionFilter

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(ScriptsListView, self).get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs

    def get_table_class(self):
        if self.request.user.is_authenticated:
            return tables.UserClocktowerTable
        return tables.ClocktowerTable


class UserScriptsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = models.ScriptVersion
    table_class = tables.UserClocktowerTable
    template_name = "scriptlist.html"
    script_view = None
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]

    def get_filterset_class(self):
        return filters.ScriptVersionFilter

    def get_queryset(self):
        queryset = super(UserScriptsListView, self).get_queryset()
        if self.script_view == "favourite":
            queryset = queryset.filter(script__favourites__user=self.request.user)
        elif self.script_view == "owned":
            queryset = queryset.filter(script__owner=self.request.user)
        return queryset

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(UserScriptsListView, self).get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs


def get_comment_data(comment: models.Comment, indent: int) -> List:
    data = []
    comment_data = {}
    comment_data["comment"] = comment
    comment_data["indent"] = indent
    data.append(comment_data)
    for child_comment in comment.children.all().order_by("created"):
        data.extend(get_comment_data(child_comment, min(indent + 1, 6)))
    return data


def get_comments(script: models.Script) -> Dict:
    comments = []
    for comment in script.comments.filter(parent__isnull=True).order_by("created"):
        comments.extend(get_comment_data(comment, 0))
    return comments


def count_character(script_content, character_type: models.CharacterType) -> int:
    count = 0
    clocktower_characters = cache.get_clocktower_characters()
    for json_entry in script_content:
        character = None
        character_id = ""
        if isinstance(json_entry, str):
            character = clocktower_characters.get(json_entry, None)
        elif isinstance(json_entry, dict):
            character_id = json_entry.get("id", "")
            if character_id == "_meta":
                continue
            character = clocktower_characters.get(character_id, None)
            if not character:
                character = cache.get_homebrew_characters().get(character_id, None)

        if character and character.character_type == character_type:
            count += 1
    return count


def calculate_edition(script_content: Dict) -> int:
    edition = models.Edition.BASE
    clocktower_characters = cache.get_clocktower_characters()
    for json_entry in script_content:
        character = None
        character_id = ""
        if isinstance(json_entry, str):
            character = clocktower_characters.get(json_entry, None)
        elif isinstance(json_entry, dict):
            character_id = json_entry.get("id", "")
            if character_id == "_meta":
                continue
            character = clocktower_characters.get(character_id, None)

        if not character:
            # We don't know what this character is, therefore this needs
            # tokens we don't know about.
            edition = models.Edition.ALL
        elif character.edition > edition:
            edition = character.edition

        if edition == models.Edition.ALL:
            return edition

    return edition


class ScriptView(generic.DetailView):
    template_name = "script.html"
    model = models.Script

    def get_queryset(self):
        return models.Script.objects.select_related("owner").prefetch_related(
            Prefetch("versions", queryset=models.ScriptVersion.objects.prefetch_related("tags").order_by("-version")),
            Prefetch(
                "comments",
                queryset=models.Comment.objects.select_related("user")
                .prefetch_related(
                    Prefetch("children", queryset=models.Comment.objects.select_related("user").order_by("created"))
                )
                .filter(parent__isnull=True)
                .order_by("created"),
            ),
            "votes",
            "favourites",
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context["active-tab"] = ""
        _messages = messages.get_messages(request)
        for message in _messages:
            context["activetab"] = message.message
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "selected_version" in self.request.GET:
            current_script = self.object.versions.get(version=self.request.GET["selected_version"])
        elif "version" in self.kwargs:
            current_script = self.object.versions.get(version=self.kwargs["version"])
        else:
            current_script = self.object.versions.order_by("-version").first()
        context["script_version"] = current_script

        changes = {}
        diff_script_version = None
        for script_version in self.object.versions.all().order_by("-version"):
            # If we're looking at an older script, don't show changes future to that.
            if script_version.version > current_script.version:
                continue

            if diff_script_version:
                changes[diff_script_version.version] = {}
                changes[diff_script_version.version]["additions"] = script_json.get_json_additions(
                    script_version.content.copy(),
                    diff_script_version.content.copy(),
                )
                changes[diff_script_version.version]["deletions"] = script_json.get_json_additions(
                    diff_script_version.content.copy(),
                    script_version.content.copy(),
                )
                changes[diff_script_version.version]["changes"] = script_json.get_json_changes(
                    script_version.content.copy(),
                    diff_script_version.content.copy(),
                )
                changes[diff_script_version.version]["previous_version"] = script_version.version
            diff_script_version = script_version

        context["changes"] = changes
        context["script_version"] = current_script
        context["comments"] = get_comments(current_script.script)
        context["languages"] = (
            models.Translation.objects.values_list("language", flat=True).distinct("language").order_by("language")
        )

        context["can_delete"] = self.request.user == current_script.script.owner
        context["script_tool_link"] = (
            f"https://script.bloodontheclocktower.com?script={script_json.compress_json(current_script.content)}"
        )
        context["bootlegger_rules"] = script_json.get_bootlegger_rules_from_json(current_script.content)

        return context


def get_all_roles(edition: models.Edition):
    roles = []
    ordering = {}
    try:
        r = requests.get("https://botc-tools.vercel.app/sao-sorter/order.json")
        ordering = r.json()
    except requests.RequestException:
        pass
    for character in models.ClocktowerCharacter.objects.all().filter(edition__lte=edition):
        roles.append(Role(character.character_id, ordering.get(character.character_id, "7")))
    roles.sort()
    return [{"id": x.character_id} for x in roles]


@dataclass
class Role:
    character_id: str
    sao_order: str

    def __lt__(self, other):
        return self.sao_order < other.sao_order


def get_edition_from_request(request):
    if "selected_edition" in request.GET:
        for possible_edition in models.Edition:
            if possible_edition.label == request.GET.get("selected_edition"):
                return possible_edition
    return models.Edition.ALL


class AllRolesScriptView(generic.TemplateView):
    template_name = "all_roles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        edition = get_edition_from_request(self.request)
        context["content"] = get_all_roles(edition)
        context["edition"] = edition
        context["editions"] = models.Edition.choices
        context["languages"] = (
            models.Translation.objects.values_list("language", flat=True).distinct("language").order_by("language")
        )
        return context


def download_all_roles_json(request, language: Optional[str] = None) -> FileResponse:
    edition = get_edition_from_request(request)
    content = get_all_roles(edition)
    content = translate_content(content, request, language)
    return json_file_response("all_roles", content)


def update_script(script_version: models.ScriptVersion, cleaned_data, author, user):
    script_version.script_type = cleaned_data["script_type"]
    script_version.author = author
    if cleaned_data.get("notes", None):
        script_version.notes = cleaned_data["notes"]
    if cleaned_data.get("pdf", None):
        # Delete old PDF if it exists to prevent orphaned files
        if script_version.pdf:
            script_version.pdf.delete(save=False)
        script_version.pdf = cleaned_data["pdf"]

    if user.is_staff:
        # Staff members can see all the tags in the form, so any changes they make
        # should actually me made.
        script_version.tags.set(cleaned_data["tags"])
    else:
        # Non-staff members can't see non-public tags so add the current non-public tags back
        current_tags = script_version.tags.filter(public=False)
        script_version.tags.set(cleaned_data["tags"] | current_tags)
    script_version.save()


class BaseScriptUploadView(generic.FormView):
    template_name = "upload.html"
    script_version = None

    def get_script(self, script_pk):
        if script_pk:
            script = models.Script.objects.get(pk=script_pk)
            return script

    def get_initial(self):
        initial = super().get_initial()
        script_pk = self.request.GET.get("script", None)
        script = self.get_script(script_pk)
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
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_form(self):
        """
        If this is an anonymous user, don't allow them to add notes.
        """
        form = super().get_form(self.form_class)

        # If this user isn't authenticated, don't allow them to add notes or upload anonymously
        # (since it will be anonymous anyway).
        if not self.request.user.is_authenticated:
            form.fields.pop("notes")
            form.fields.pop("anonymous")
        else:
            script_pk = self.request.GET.get("script", None)
            if script_pk:
                script = models.Script.objects.get(pk=script_pk)

                # If this script is owned by someone, and it is not the currently logged in
                # user, don't show the notes field.
                if script and script.owner and (script.owner != self.request.user):
                    form.fields.pop("notes")

                # If this is an update to an existing script, we can't make it anonymous.
                if script:
                    form.fields.pop("anonymous")
                    form.fields.get("name").disabled = True

        return form


class ScriptUploadView(BaseScriptUploadView):
    form_class = forms.ScriptForm

    def get_initial(self):
        initial = super().get_initial()
        initial["tags"] = []
        script_pk = self.request.GET.get("script", None)
        script = self.get_script(script_pk)
        if script:
            script_version = script.latest_version()
            if script_version.tags:
                initial["tags"] = script_version.tags.all()

        tags = self.request.GET.getlist("tags", [])
        for tag in tags:
            try:
                initial["tags"].append(models.ScriptTag.objects.get(pk=tag))
            except models.ScriptTag.DoesNotExist:
                continue

        return initial

    def get_form(self):
        form = super().get_form()
        if self.request.user.is_staff:
            if form.fields.get("tags"):
                form.fields.get("tags").queryset = models.ScriptTag.objects.all().order_by("order")
        return form

    def get_success_url(self):
        return "/script/" + str(self.script_version.script.pk)

    def form_valid(self, form):
        user = self.request.user
        json = script_json.get_json_content(form.cleaned_data)
        is_latest = True
        current_tags = None

        # Temporarily remove getting information from the _meta fields due to them
        # not including spaces.
        # https://github.com/AdmiralGT/botc-scripts/issues/220

        # Use the script name from the JSON in preference of the text field.
        # script_name = script_json.get_name_from_json(json)
        # if not script_name:
        #     script_name = form.cleaned_data["name"]
        script_name = form.cleaned_data["name"]

        # Either get the current script, or create a new one based on the name.
        script, created = models.Script.objects.get_or_create(name=script_name)

        # We only want to set the owner on newly created scripts, so if we've
        # just created the script and the user is authenticated, set the owner to this user
        # unless they uploaded anonymously.
        # It's possible the user is uploading a "new" script by uploading a new version
        # of an existing script with a new name. In this instance, the anonymous field
        # isn't present, so default that this is anonymous.
        if created and user.is_authenticated and not form.cleaned_data.get("anonymous", True):
            script.owner = user
            script.save()

        # Temporarily remove getting information from the _meta fields due to them
        # not including spaces.
        # https://github.com/AdmiralGT/botc-scripts/issues/220

        # Use the author in the JSON in preference of the text field.
        # author = script_json.get_author_from_json(json)
        # if not author:
        #     author = form.cleaned_data["author"]
        author = form.cleaned_data["author"]

        # If the script object has not just been created, we're either updating an existing version of the script
        # or we're uploading a new version of the script.
        if not created:
            try:
                script_version = models.ScriptVersion.objects.get(script=script, version=form.cleaned_data["version"])
                # We're updating an existing version of a script.
                # Our validation should have caught not being able to upload different
                # JSON content for this script.
                update_script(script_version, form.cleaned_data, author, user)
                self.script_version = script_version
                return HttpResponseRedirect(self.get_success_url())
            except models.ScriptVersion.DoesNotExist:
                # We're uploading a new version of this script.
                if script.latest_version():
                    # We need to protect this code against instances where a script doesn't
                    # have a latest version.
                    if script.latest_version().content == json:
                        # The content hasn't change from the latest version, so just update
                        # the script and exit, the user probably made an error in changing
                        # the version string.
                        update_script(script.latest_version(), form.cleaned_data, author, user)
                        self.script_version = script.latest_version()
                        return HttpResponseRedirect(self.get_success_url())

                    if Version(form.cleaned_data["version"]) > script.latest_version().version:
                        # This is newer than the latest version, so set that
                        # version to not be latest.
                        current_tags = script.latest_version().tags
                        latest_version = script.latest_version()
                        latest_version.latest = False
                        latest_version.save()
                    else:
                        # We're uploading an older version than the latest, so don't mark this version
                        # as the latest, that's still the current latest.
                        is_latest = False

        homebrewiness = create_characters_and_determine_homebrew_status(json, script)

        num_townsfolk = count_character(json, models.CharacterType.TOWNSFOLK)
        num_outsiders = count_character(json, models.CharacterType.OUTSIDER)
        num_minions = count_character(json, models.CharacterType.MINION)
        num_demons = count_character(json, models.CharacterType.DEMON)
        num_fabled = count_character(json, models.CharacterType.FABLED)
        num_loric = count_character(json, models.CharacterType.LORIC)
        num_travellers = count_character(json, models.CharacterType.TRAVELLER)
        edition = calculate_edition(json)

        # Create the Script Version object from the form.
        self.script_version = models.ScriptVersion.objects.create(
            version=form.cleaned_data["version"],
            script_type=form.cleaned_data["script_type"],
            content=json,
            script=script,
            pdf=form.cleaned_data["pdf"],
            author=author,
            latest=is_latest,
            num_townsfolk=num_townsfolk,
            num_outsiders=num_outsiders,
            num_minions=num_minions,
            num_demons=num_demons,
            num_fabled=num_fabled,
            num_loric=num_loric,
            num_travellers=num_travellers,
            edition=edition,
            homebrewiness=homebrewiness,
        )
        if form.cleaned_data.get("notes", None):
            self.script_version.notes = form.cleaned_data["notes"]
            self.script_version.save()

        # Set the tags to be what the form indicates should be set
        self.script_version.tags.set(form.cleaned_data["tags"])

        # Re-add public tags that are inheritable and haven't been included
        if current_tags:
            for tag in current_tags.all():
                # If the tag is public, and wasn't included in the form
                # or the tag is not inheritable, remove it from the tags to
                # add.
                if tag.public and tag not in form.cleaned_data["tags"] or not tag.inheritable:
                    current_tags.remove(tag)
            self.script_version.tags.add(*current_tags.all())

        if homebrewiness == models.Homebrewiness.HYBRID:
            try:
                hybrid_tag = models.ScriptTag.objects.get(name="Hybrid Script")
                self.script_version.tags.add(hybrid_tag)
            except models.ScriptTag.DoesNotExist:
                pass
        elif homebrewiness == models.Homebrewiness.HOMEBREW:
            try:
                homebrew_tag = models.ScriptTag.objects.get(name="Homebrew Script")
                self.script_version.tags.add(homebrew_tag)
            except models.ScriptTag.DoesNotExist:
                pass

        return HttpResponseRedirect(self.get_success_url())


class ScriptDeleteView(LoginRequiredMixin, generic.edit.BaseDeleteView):
    """
    Deletes a script version.
    """

    model = models.Script

    def form_valid(self, form):
        self.object: models.Script = self.get_object()
        script: models.Script = self.object
        try:
            script_version: models.ScriptVersion = script.versions.all().get(version=self.kwargs.get("version"))
        except models.ScriptVersion.DoesNotExist:
            raise Http404("Cannot delete a script version that does not exist.")

        if script.owner != self.request.user:
            return HttpResponseForbidden()
        script_version.delete()

        if script.versions.count() > 0:
            latest_version = script.latest_version()
            latest_version.latest = True
            latest_version.save()
            self.success_url = self.determine_success_url(script)
        else:
            script.delete()
            self.success_url = "/"

        return HttpResponseRedirect(self.get_success_url())

    def determine_success_url(self, script):
        return f"/script/{script.pk}"


class StatisticsView(generic.ListView, FilterView):
    model = models.ScriptVersion
    template_name = "statistics.html"
    filterset_class = filters.StatisticsFilter

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.object_list = super().get_queryset()
        context = super().get_context_data(**kwargs)
        stats_character = None
        characters_to_display = 25

        if "all" in self.request.GET:
            queryset = models.ScriptVersion.objects.all()
        else:
            queryset = models.ScriptVersion.objects.filter(latest=True)
        queryset = queryset.filter(homebrewiness=models.Homebrewiness.CLOCKTOWER)

        if self.request.user.is_authenticated:
            context["filter"] = self.get_filterset(self.get_filterset_class())
            if "is_owner" in self.request.GET:
                queryset = queryset.filter(script__owner=self.request.user)

        if "character" in self.kwargs:
            try:
                stats_character = models.ClocktowerCharacter.objects.get(character_id=self.kwargs.get("character"))
                queryset = queryset.filter(content__contains=[{"id": stats_character.character_id}])
            except models.ClocktowerCharacter.DoesNotExist:
                raise Http404()
        elif "tags" in self.kwargs:
            tags = models.ScriptTag.objects.get(pk=self.kwargs.get("tags"))
            if tags:
                queryset = models.ScriptVersion.objects.filter(tags__in=[tags])

        if "tags" in self.request.GET:
            try:
                tags = models.ScriptTag.objects.get(pk=self.request.GET.get("tags"))
                if tags:
                    queryset = queryset.filter(tags__in=[tags])
            except ValueError:
                pass

        if "num" in self.request.GET:
            try:
                if int(self.request.GET.get("num")):
                    characters_to_display = int(self.request.GET.get("num"))
                    if characters_to_display < 1:
                        characters_to_display = 25
            except ValueError:
                pass

        if "edition" in self.request.GET:
            try:
                edition = models.Edition(int(self.request.GET.get("edition")))
                queryset = queryset.filter(edition__lte=edition)
            except ValueError:
                pass

        context["total"] = queryset.count()
        if queryset.count() == 0:
            return context

        character_count = {}
        num_count = {}
        for type in models.CharacterType:
            character_count[type.value] = Counter()
            num_count[type.value] = Counter()

        for character in models.ClocktowerCharacter.objects.all():
            # If we're on a Character Statistics page, don't include this character in the count.
            if character == stats_character:
                continue

            character_count[character.character_type][character] = queryset.filter(
                content__contains=[{"id": character.character_id}]
            ).count()

        for type in models.CharacterType:
            context[type.value] = character_count[type.value].most_common(characters_to_display)
            context[type.value + "least"] = character_count[type.value].most_common()[
                : ((characters_to_display + 1) * -1) : -1
            ]

        character_count_fields = {
            "num_townsfolk": models.CharacterType.TOWNSFOLK.value,
            "num_outsiders": models.CharacterType.OUTSIDER.value,
            "num_minions": models.CharacterType.MINION.value,
            "num_demons": models.CharacterType.DEMON.value,
            "num_travellers": models.CharacterType.TRAVELLER.value,
            "num_fabled": models.CharacterType.FABLED.value,
            "num_loric": models.CharacterType.LORIC.value,
        }

        for field, label in character_count_fields.items():
            result = (
                queryset.values(field)
                .annotate(script_count=Count(field), character_count=F(field))
                .order_by("character_count")
            )
            for row in result:
                num_count[label][str(row["character_count"])] = row["script_count"]

        for type in models.CharacterType:
            num_count[type.value] = dict(num_count[type.value])
        context["num_count"] = num_count
        context["stats_character"] = stats_character

        return context


class UserDeleteView(LoginRequiredMixin, generic.TemplateView):
    """
    Deletes the currently signed-in user.
    """

    template_name = "account/delete.html"

    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        return HttpResponseRedirect("/")


def get_script(request, pk: int) -> models.Script:
    try:
        script = models.Script.objects.get(pk=pk)
    except models.Script.DoesNotExist:
        return redirect(request.POST["next"])
    return script


def update_user_related_script(model, user: User, script: models.Script) -> None:
    if user.is_authenticated:
        if model.objects.filter(user=user, parent=script).exists():
            object = model.objects.get(user=user, parent=script)
            object.delete()
        else:
            model.objects.create(user=user, parent=script)


def vote_for_script(request, pk: int) -> None:
    if request.method != "POST":
        raise Http404()
    script = get_script(request, pk)
    update_user_related_script(models.Vote, request.user, script)
    return redirect(request.POST["next"])


def map_similar_scripts(data):
    return {
        "value": data[1],
        "name": data[0].script.name,
        "scriptPK": data[0].script.pk,
    }


# Seperate call to calculate similar scripts so we can lazy load it
def get_similar_scripts(request, pk: int, version: str) -> JsonResponse:
    if request.method != "GET":
        raise Http404()

    current_script = models.ScriptVersion.objects.filter(script=pk, version=version)[0]

    similarity = {}
    similarity[models.ScriptTypes.TEENSYVILLE.value] = {}
    similarity[models.ScriptTypes.FULL.value] = {}
    for script_version in models.ScriptVersion.objects.filter(
        latest=True, homebrewiness=models.Homebrewiness.CLOCKTOWER
    ).order_by("pk"):
        if current_script == script_version:
            continue

        similarity[script_version.script_type][script_version] = script_json.get_similarity(
            current_script.content,
            script_version.content,
            current_script.script_type == script_version.script_type,
        )
    teensville_scripts = map(
        map_similar_scripts,
        sorted(
            similarity[models.ScriptTypes.TEENSYVILLE].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10],
    )

    full_scripts = map(
        map_similar_scripts,
        sorted(
            similarity[models.ScriptTypes.FULL].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10],
    )

    return JsonResponse({"full": list(full_scripts), "teensyville": list(teensville_scripts)})


def favourite_script(request, pk: int) -> None:
    if request.method != "POST":
        raise Http404()
    script = get_script(request, pk)
    update_user_related_script(models.Favourite, request.user, script)
    return redirect(request.POST["next"])


def translate_character(character_id: str, language: str) -> Dict:
    try:
        character = models.ClocktowerCharacter.objects.get(character_id=character_id)
    except models.ClocktowerCharacter.DoesNotExist:
        return {}

    original_character = character.full_character_json()
    try:
        translation = models.Translation.objects.get(character_id=character_id, language=language)
        translated_character = translation.full_character_json()
    except models.Translation.DoesNotExist:
        return original_character

    return_object = {**original_character, **translated_character}
    return return_object


def translate_json_content(json_content: List, language: str):
    translated_content = []
    for character_id in json_content:
        if character_id.get("id") == "_meta":
            translated_content.append(character_id)
            continue
        translated_content.append(translate_character(character_id.get("id"), language))
    return translated_content


def translate_content(content, request, language):
    if language or request.GET.get("language_select"):
        language = language if language else request.GET.get("language_select")
        return translate_json_content(content, language)
    return content


def json_file_response(name, content):
    json = js.JSONEncoder(ensure_ascii=False).encode(content)
    temp_file = TemporaryFile()
    temp_file.write(json.encode("utf-8"))
    temp_file.flush()
    temp_file.seek(0)
    response = FileResponse(temp_file, as_attachment=True, filename=(name + ".json"))
    return response


def download_json(request, pk: int, version: str, language: Optional[str] = None) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    content = translate_content(script_version.content, request, language)
    script.num_downloads = F("num_downloads") + 1
    script.save()

    return json_file_response(script.name, content)


@permission_required("scripts.download_unsupported_json")
def download_unsupported_json(request, pk: int, version: str) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    content = []
    for character_json in script_version.content:
        if character_json.get("id") == "__meta":
            content.append(character_json)
            continue

        try:
            character = models.ClocktowerCharacter.objects.get(character_id=character_json.get("id"))
            if character.edition == models.Edition.ALL:
                content.append(character.full_character_json())
            else:
                content.append(character_json)
        except models.ClocktowerCharacter.DoesNotExist:
            content.append(character_json)

    return json_file_response(script.name, content)


def download_pdf(request, pk: int, version: str) -> FileResponse:
    script = models.Script.objects.get(pk=pk)
    script_version = script.versions.get(version=version)
    if os.environ.get("DJANGO_HOST", None):
        return FileResponse(script_version.pdf, as_attachment=True)
    else:
        return FileResponse(open(script_version.pdf.name, "rb"), as_attachment=True)


class CollectionScriptListView(SingleTableView):
    model = models.ScriptVersion
    template_name = "collection.html"
    table_pagination = {"per_page": 20}
    ordering = ["pk"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collection"] = models.Collection.objects.get(pk=self.kwargs["pk"])
        return context

    def get_table_class(self):
        collection = models.Collection.objects.get(pk=self.kwargs["pk"])
        if self.request.user == collection.owner:
            return tables.CollectionClocktowerTable
        elif self.request.user.is_authenticated:
            return tables.UserClocktowerTable
        return tables.ClocktowerTable

    def get_queryset(self):
        collection = models.Collection.objects.get(pk=self.kwargs["pk"])
        return collection.scripts.order_by("pk")


class CollectionListView(SingleTableMixin, FilterView):
    model = models.Collection
    template_name = "collection_list.html"
    table_pagination = {"per_page": 20}
    ordering = ["pk"]
    table_class = tables.CollectionTable
    filterset_class = filters.CollectionFilter


class CollectionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    template_name = "upload.html"
    form_class = forms.CollectionForm
    model = models.Collection

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return "/collection/" + str(self.object.id)


class CollectionEditView(LoginRequiredMixin, generic.edit.UpdateView):
    template_name = "upload.html"
    form_class = forms.CollectionForm
    model = models.Collection

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return "/collection/" + str(self.object.id)

    def get(self, request, *args, **kwargs):
        """
        A user should only be able to edit the collections they own.
        """
        self.object = self.get_object()
        if self.object.owner != self.request.user:
            raise Http404("Cannot edit a collection you don't own.")
        return super(CollectionEditView, self).get(request, *args, **kwargs)


class CollectionDeleteView(LoginRequiredMixin, generic.edit.BaseDeleteView):
    """
    Deletes a collection.
    """

    model = models.Collection

    def get_success_url(self) -> str:
        return "/"

    def form_valid(self, form):
        self.object = self.get_object()
        if self.object.owner != self.request.user:
            raise Http404("Cannot delete a collection you don't own.")
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class AddScriptToCollectionView(LoginRequiredMixin, generic.View):
    """
    Adds a script to a collection.
    """

    def post(self, request, *args, **kwargs):
        collection = models.Collection.objects.get(pk=request.POST.get("collection"))
        script = models.ScriptVersion.objects.get(pk=request.POST.get("script_version"))
        collection.scripts.add(script)
        return HttpResponseRedirect("/script/" + str(script.script.pk) + "/" + str(script.version))


class RemoveScriptFromCollectionView(LoginRequiredMixin, generic.View):
    """
    Removes a script from a collection.
    """

    def post(self, request, *args, **kwargs):
        try:
            collection = models.Collection.objects.get(pk=kwargs["collection"])
        except models.Collection.DoesNotExist:
            raise Http404("Unknown collection.")

        if collection.owner != self.request.user:
            raise Http404("Cannot edit a collection you don't own.")

        try:
            script = models.ScriptVersion.objects.get(pk=kwargs["script"])
        except models.ScriptVersion.DoesNotExist:
            raise Http404("Unknown script.")

        collection.scripts.remove(script)
        return HttpResponseRedirect(f"/collection/{collection.pk}")


class CommentCreateView(LoginRequiredMixin, generic.View):
    """
    Creates comments on scripts.
    """

    def post(self, request, *args, **kwargs):
        parent = None
        try:
            script = models.Script.objects.get(pk=request.POST["script"])
        except models.Script.DoesNotExist:
            return HttpResponseRedirect("/")

        redirect_url = f"/script/{script.pk}"

        if request.POST.get("parent"):
            try:
                parent = models.Comment.objects.get(pk=request.POST["parent"])
            except models.Comment.DoesNotExist:
                return HttpResponseRedirect(redirect_url)

        if request.POST["comment"]:
            if parent:
                models.Comment.objects.create(
                    user=request.user,
                    comment=request.POST["comment"],
                    script=script,
                    parent=parent,
                )
            else:
                models.Comment.objects.create(user=request.user, comment=request.POST["comment"], script=script)
        messages.success(request, "comments-tab")
        return HttpResponseRedirect(redirect_url)


class CommentEditView(LoginRequiredMixin, generic.View):
    """
    Edits a comment.
    """

    def post(self, request, *args, **kwargs):
        if request.POST["comment"]:
            comment = models.Comment.objects.get(pk=kwargs["pk"])

            if comment.user != request.user:
                raise Http404("Cannot edit a comment you did not create.")

            comment.comment = request.POST["comment"]
            comment.save()

        messages.success(request, "comments-tab")

        success_url = f"/script/{comment.script.pk}"
        return HttpResponseRedirect(success_url)


class CommentDeleteView(LoginRequiredMixin, generic.View):
    """
    Removes a script from a collection.
    """

    def post(self, request, *args, **kwargs):
        comment = models.Comment.objects.get(pk=kwargs["pk"])

        if comment.user != request.user:
            raise Http404("Cannot delete a comment you did not make.")

        if comment.parent:
            # If this comment has a parent then update all our child comments to point
            # to that same parent.
            for child in comment.children.all():
                child.parent = comment.parent
                child.save()

        success_url = f"/script/{comment.script.pk}"
        comment.delete()
        messages.success(request, "comments-tab")
        return HttpResponseRedirect(success_url)


class AdvancedSearchResultsView(SingleTableView):
    model = models.ScriptVersion
    template_name = "scriptlist.html"
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]
    script_view = None

    def get_queryset(self):
        cache_key = self.request.GET.get("key")
        if cache_key:
            data = cache.get_advanced_search_results(cache_key)
            if data:
                if data.get("num_results") == 0:
                    return models.ScriptVersion.objects.none()
                ids = data.get("queryset_pks", [])
                order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
                queryset = models.ScriptVersion.objects.filter(pk__in=ids).order_by(order)
                return queryset
        return models.ScriptVersion.objects.all()

    def get_table_class(self):
        if self.request.user.is_authenticated:
            return tables.UserClocktowerTable
        return tables.ClocktowerTable


class AdvancedSearchView(generic.FormView, SingleTableMixin):
    template_name = "advanced_search.html"
    form_class = forms.AdvancedSearchForm
    script_version = None

    def get_form(self):
        # This dynamic calculation is very slow and probably isn't worth it, so instead we just use a fixed value of
        # 0 to 25.
        # townsfolk = models.ScriptVersion.objects.all().order_by("num_townsfolk")
        # townsfolk_choices = [(i, i) for i in range(townsfolk.first().num_townsfolk, townsfolk.last().num_townsfolk + 1)]
        # outsider = models.ScriptVersion.objects.all().order_by("num_outsiders")
        # outsider_choices = [(i, i) for i in range(outsider.first().num_outsiders, outsider.last().num_outsiders + 1)]
        # minion = models.ScriptVersion.objects.all().order_by("num_minions")
        # minion_choices = [(i, i) for i in range(minion.first().num_minions, minion.last().num_minions + 1)]
        # demon = models.ScriptVersion.objects.all().order_by("num_demons")
        # demon_choices = [(i, i) for i in range(demon.first().num_demons, demon.last().num_demons + 1)]
        # fabled = models.ScriptVersion.objects.all().order_by("num_fabled")
        # fabled_choices = [(i, i) for i in range(fabled.first().num_fabled, fabled.last().num_fabled + 1)]
        # travellers = models.ScriptVersion.objects.all().order_by("num_travellers")
        # traveller_choices = [
        #     (i, i) for i in range(travellers.first().num_travellers, travellers.last().num_travellers + 1)
        # ]

        return forms.AdvancedSearchForm(
            townsfolk_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            outsider_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            minion_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            demon_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            fabled_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            loric_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            traveller_choices=[(i, i) for i in range(constants.MAX_CHARACTER_COUNT + 1)],
            **self.get_form_kwargs(),
        )

    def form_valid(self, form):
        all_scripts = form.cleaned_data.get("all_scripts", False)
        if all_scripts:
            queryset = models.ScriptVersion.objects.all()
        else:
            queryset = models.ScriptVersion.objects.filter(latest=True)

        include_hybrid = form.cleaned_data.get("include_hybrid", False)
        if not include_hybrid:
            queryset = queryset.exclude(homebrewiness=models.Homebrewiness.HYBRID)

        include_homebrew = form.cleaned_data.get("include_homebrew", False)
        if not include_homebrew:
            queryset = queryset.exclude(homebrewiness=models.Homebrewiness.HOMEBREW)

        script_type = form.cleaned_data.get("script_type")
        if script_type == models.ScriptTypes.TEENSYVILLE:
            queryset = queryset.exclude(script_type=models.ScriptTypes.FULL)
        else:
            queryset = queryset.exclude(script_type=models.ScriptTypes.TEENSYVILLE)

        if form.cleaned_data.get("name"):
            queryset = queryset.annotate(
                name_similarity=TrigramSimilarity("script__name", form.cleaned_data.get("name"))
            )
            queryset = queryset.filter(name_similarity__gt=0).order_by("-name_similarity")
        if form.cleaned_data.get("author"):
            queryset = queryset.annotate(author_similarity=TrigramSimilarity("author", form.cleaned_data.get("author")))
            queryset = queryset.filter(author_similarity__gt=0).order_by("-author_similarity")

        if form.cleaned_data.get("includes_characters"):
            queryset = filters.include_characters(queryset, form.cleaned_data.get("includes_characters"))
        if form.cleaned_data.get("excludes_characters"):
            queryset = filters.exclude_characters(queryset, form.cleaned_data.get("excludes_characters"))

        queryset = queryset.filter(edition__lte=form.cleaned_data.get("edition"))
        tag_combination = form.cleaned_data.get("tag_combinations")
        if tag_combination == "AND":
            for tag in form.cleaned_data.get("tags"):
                queryset = queryset.filter(tags=tag)
        else:
            if form.cleaned_data.get("tags"):
                queryset = queryset.filter(tags__in=form.cleaned_data.get("tags"))

        if form.cleaned_data.get("number_of_townsfolk"):
            queryset = queryset.filter(num_townsfolk__in=form.cleaned_data.get("number_of_townsfolk"))

        if form.cleaned_data.get("number_of_outsiders"):
            queryset = queryset.filter(num_outsiders__in=form.cleaned_data.get("number_of_outsiders"))

        if form.cleaned_data.get("number_of_minions"):
            queryset = queryset.filter(num_minions__in=form.cleaned_data.get("number_of_minions"))

        if form.cleaned_data.get("number_of_demons"):
            queryset = queryset.filter(num_demons__in=form.cleaned_data.get("number_of_demons"))

        if form.cleaned_data.get("number_of_fabled"):
            queryset = queryset.filter(num_fabled__in=form.cleaned_data.get("number_of_fabled"))

        if form.cleaned_data.get("number_of_travellers"):
            queryset = queryset.filter(num_travellers__in=form.cleaned_data.get("number_of_travellers"))

        if form.cleaned_data.get("number_of_loric"):
            queryset = queryset.filter(num_loric__in=form.cleaned_data.get("number_of_loric"))

        if form.cleaned_data.get("minimum_number_of_likes"):
            queryset = queryset.annotate(score=Count("script__votes"))
            queryset = queryset.filter(score__gte=form.cleaned_data.get("minimum_number_of_likes"))

        if form.cleaned_data.get("minimum_number_of_favourites"):
            queryset = queryset.annotate(num_favs=Count("script__favourites"))
            queryset = queryset.filter(num_favs__gte=form.cleaned_data.get("minimum_number_of_favourites"))

        if form.cleaned_data.get("minimum_number_of_comments"):
            queryset = queryset.annotate(num_comments=Count("script__comments"))
            queryset = queryset.filter(num_comments__gte=form.cleaned_data.get("minimum_number_of_comments"))

        queryset = queryset.order_by("-pk")
        pk_list = list(queryset.values_list("pk", flat=True))
        cache_key = cache.store_advanced_search_results(pk_list)

        return redirect(f"/script/search/results?key={cache_key}")


class HealthCheckView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


class UpdateDatabaseView(LoginRequiredMixin, generic.FormView):
    """
    Updates scripts in the database.
    """

    template_name = "update_database.html"
    form_class = forms.UpdateDatabaseForm
    success_url = "/update"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.request.user.is_staff:
            return redirect("")

        start = form.cleaned_data.get("start", 0)
        end = form.cleaned_data.get("end", 0)

        for i in range(start, end + 1):
            try:
                script = models.ScriptVersion.objects.get(pk=i)
                script.content = script_json.strip_special_characters_from_json(script.content)
                script.save()
            except models.ScriptVersion.DoesNotExist:
                # It's quite possible some script numbers don't exist, so just continue
                continue

        return HttpResponseRedirect(self.get_success_url())


def get_character_type_from_team(team):
    match team:
        case "townsfolk":
            return models.CharacterType.TOWNSFOLK
        case "outsider":
            return models.CharacterType.OUTSIDER
        case "minion":
            return models.CharacterType.MINION
        case "demon":
            return models.CharacterType.DEMON
        case "traveler" | "traveller":
            return models.CharacterType.TRAVELLER
        case "fabled":
            return models.CharacterType.FABLED
        case "loric":
            return models.CharacterType.LORIC
        case _:
            return models.CharacterType.UNKNOWN


def character_missing_from_database(character_id, roles):
    for role in roles:
        if character_id == role.get("id", "UNKNOWN CHARACTER"):
            return True
    return False


def create_characters_and_determine_homebrew_status(script_content: Dict, script: models.Script):
    homebrewiness = models.Homebrewiness.CLOCKTOWER
    non_clocktower_characters = 0
    entries_to_ignore = 0
    roles = []
    try:
        roles = requests.get("https://script.bloodontheclocktower.com/data/roles.json", timeout=2)
    except requests.exceptions.Timeout:
        pass

    for item in script_content:
        if item.get("id", "") == "_meta":
            entries_to_ignore += 1
            continue

        try:
            character = models.ClocktowerCharacter.objects.get(character_id=item.get("id", ""))
            # Ignore the use of the official Bootlegger character, this indicates the script
            # hybrid/homebrew already but shouldn't count against homebrew status.
            if character.character_id == "bootlegger":
                entries_to_ignore += 1
        except models.ClocktowerCharacter.DoesNotExist:
            if roles.ok and character_missing_from_database(item.get("id", ""), js.loads(roles.content)):
                # It's possible we don't know about this character because it has just been released
                # and it's not been added to the database. In this case check the script tool for roles
                # and if it present, don't mark this as a homebrew character.
                continue
            if len(item.keys()) == 1:
                # If the character element has more than 1 key then it is almost certainly an attempt at a
                # homebrew/hybrid character, otherwise it's probably official.
                continue

            non_clocktower_characters += 1

            image_url = item.get("image")
            if isinstance(image_url, list):
                image_url = ",".join(image_url)
            try:
                homebrew_character = models.HomebrewCharacter.objects.get(character_id=item.get("id"))
                if homebrew_character.script and homebrew_character.script == script:
                    models.HomebrewCharacter.objects.update_or_create(
                        character_id=item.get("id"),
                        script=script,
                        defaults={
                            "character_name": item.get("name"),
                            "image_url": image_url,
                            "character_type": get_character_type_from_team(item.get("team")).value,
                            "ability": item.get("ability"),
                            "first_night_position": item.get("firstNight", None),
                            "other_night_position": item.get("otherNight", None),
                            "first_night_reminder": item.get("firstNightReminder", None),
                            "other_night_reminder": item.get("otherNightReminder", None),
                            "global_reminders": ",".join(item.get("remindersGlobal", [])),
                            "reminders": ",".join(item.get("reminders", [])),
                            "modifies_setup": item.get("setup", False),
                        },
                    )
                else:
                    models.HomebrewCharacter.objects.update_or_create(
                        character_id=item.get("id"),
                        defaults={
                            "script": script,
                            "character_name": item.get("name"),
                            "image_url": image_url,
                            "character_type": get_character_type_from_team(item.get("team")).value,
                            "ability": item.get("ability"),
                            "first_night_position": item.get("firstNight", None),
                            "other_night_position": item.get("otherNight", None),
                            "first_night_reminder": item.get("firstNightReminder", None),
                            "other_night_reminder": item.get("otherNightReminder", None),
                            "global_reminders": ",".join(item.get("remindersGlobal", [])),
                            "reminders": ",".join(item.get("reminders", [])),
                            "modifies_setup": item.get("setup", False),
                        },
                    )
            except models.HomebrewCharacter.DoesNotExist:
                models.HomebrewCharacter.objects.create(
                    character_id=item.get("id"),
                    script=script,
                    character_name=item.get("name"),
                    image_url=image_url,
                    character_type=get_character_type_from_team(item.get("team")).value,
                    ability=item.get("ability"),
                    first_night_position=item.get("firstNight", None),
                    other_night_position=item.get("otherNight", None),
                    first_night_reminder=item.get("firstNightReminder", None),
                    other_night_reminder=item.get("otherNightReminder", None),
                    global_reminders=",".join(item.get("remindersGlobal", [])),
                    reminders=",".join(item.get("reminders", [])),
                    modifies_setup=item.get("setup", False),
                )

    if non_clocktower_characters == len(script_content) - entries_to_ignore:
        homebrewiness = models.Homebrewiness.HOMEBREW
    elif non_clocktower_characters > 0:
        homebrewiness = models.Homebrewiness.HYBRID

    return homebrewiness
