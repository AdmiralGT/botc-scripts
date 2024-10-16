from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from scripts import views, script_json
from homebrew import filters, tables, models, forms
from scripts import models as s_models
from django.http import (
    HttpResponseRedirect,
)

def get_character_type_from_team(team):
    match team:
        case "townsfolk":
            return models.HomebrewCharacterType.TOWNSFOLK
        case "outsider":
            return models.HomebrewCharacterType.OUTSIDER
        case "minion":
            return models.HomebrewCharacterType.MINION
        case "demon":
            return models.HomebrewCharacterType.DEMON
        case "traveler" | "traveller":
            return models.HomebrewCharacterType.TRAVELLER
        case "fabled":
            return models.HomebrewCharacterType.FABLED
        case _:
            return models.HomebrewCharacterType.UNKNOWN
        

def create_characters_and_determine_homebrew_status(json):
    homebrewiness = models.Homebrewiness.HOMEBREW
    for item in json:
        if isinstance(item, str):
            homebrewiness = models.Homebrewiness.HYBRID
        elif isinstance(item, dict):
            if item.get("id", "") == "_meta":
                continue

            models.HomebrewCharacter.objects.update_or_create(
                character_id=item.get("id"),
                character_name=item.get("name"),
                image_url=" ".join(item.get("image")),
                character_type=get_character_type_from_team(item.get("team")),
                ability=item.get("ability"),
                first_night_position=item.get("firstNight", None),
                other_night_position=item.get("otherNight", None),
                first_night_reminder=item.get("firstNightReminder", None),
                other_night_reminder=item.get("otherNightReminder", None),
                global_reminder=" ".join(item.get("remindersGlobal")),
                reminders=" ".join(item.get("reminders")),
                modifies_setup=item.get("setup", False),
            )

    return homebrewiness


class HomebrewListView(SingleTableMixin, FilterView):
    model = models.HomebrewVersion
    template_name = "scriptlist.html"
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]
    script_view = None

    def get_filterset_class(self):
        if self.request.user.is_authenticated:
            return filters.FavouriteHomebrewVersionFilter
        return filters.HomebrewVersionFilter

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(HomebrewListView, self).get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs

    def get_table_class(self):
        if self.request.user.is_authenticated:
            return tables.UserHomebrewTable
        return tables.HomebrewTable

class HomebrewScriptView(views.ScriptView):
    template_name = "homebrew/script.html"

class HomebrewDeleteView(views.ScriptDeleteView):
    def determine_success_url(self, script):
        return f"/homebrew/script/{script.pk}"

class HomebrewUploadView(views.BaseScriptUploadView):
    form_class = forms.HomebrewForm

    def get_success_url(self):
        return "/script/" + str(self.script_version.script.pk)

    def form_valid(self, form):
        user = self.request.user
        # geoffthomas Not sure I want to convert format anymore
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
        if (
            created
            and user.is_authenticated
            and not form.cleaned_data.get("anonymous", True)
        ):
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
                script_version = models.HomebrewVersion.objects.get(
                    script=script, version=form.cleaned_data["version"]
                )
                # We're updating an existing version of a script.
                # Our validation should have caught not being able to upload different
                # JSON content for this script.
                update_script(script_version, form.cleaned_data, author, user)
                self.script_version = script_version
                return HttpResponseRedirect(self.get_success_url())
            except models.HomebrewVersion.DoesNotExist:
                # We're uploading a new version of this script.
                if script.latest_version():
                    # We need to protect this code against instances where a script doesn't
                    # have a latest version.
                    if script.latest_version().content == json:
                        # The content hasn't change from the latest version, so just update
                        # the script and exit, the user probably made an error in changing
                        # the version string.
                        update_script(
                            script.latest_version(), form.cleaned_data, author, user
                        )
                        self.script_version = script.latest_version()
                        return HttpResponseRedirect(self.get_success_url())

                    if (
                        Version(form.cleaned_data["version"])
                        > script.latest_version().version
                    ):
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

        homebrewiness = create_characters_and_determine_homebrew_status(json)
        num_townsfolk = count_character(json, models.HomebrewCharacterType.TOWNSFOLK)
        num_outsiders = count_character(json, models.HomebrewCharacterType.OUTSIDER)
        num_minions = count_character(json, models.HomebrewCharacterType.MINION)
        num_demons = count_character(json, models.HomebrewCharacterType.DEMON)
        num_fabled = count_character(json, models.HomebrewCharacterType.FABLED)
        num_travellers = count_character(json, models.HomebrewCharacterType.TRAVELLER)

        # Create the Script Version object from the form.
        self.script_version = models.HomebrewVersion.objects.create(
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
            num_travellers=num_travellers,
            homebrewiness=homebrewiness,
        )
        if form.cleaned_data.get("notes", None):
            self.script_version.notes = form.cleaned_data["notes"]
            self.script_version.save()

        return HttpResponseRedirect(self.get_success_url())


def count_character(script_content, character_type: models.HomebrewCharacterType) -> int:
    count = 0
    for json_entry in script_content:
        if isinstance(json_entry, str):
            try:
                character = s_models.ClocktowerCharacter.objects.get(character_id=json_entry)
            except s_models.ClocktowerCharacter.DoesNotExist:
                continue
        elif isinstance(json_entry, dict):
            try:
                character = s_models.ClocktowerCharacter.objects.get(character_id=json_entry.get("id"))
                if character and character.character_type == character_type:
                    count += 1
            except s_models.ClocktowerCharacter.DoesNotExist:
                try:
                    homebrew = models.HomebrewCharacter.objects.get(character_id=json_entry.get("id"))
                    if homebrew and homebrew.character_type == character_type:
                        count += 1
                except models.HomebrewCharacter.DoesNotExist:
                    continue
    return count
