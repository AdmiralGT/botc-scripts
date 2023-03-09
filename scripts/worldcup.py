from django.views import generic
from scripts import models, views
from typing import Dict, Any
from collections import Counter


class WorldCupView(generic.TemplateView):
    template_name = "worldcup/fixtures.html"

    def get_world_cup_script(self, script: models.Script):
        for version in script.versions.all():
            if models.ScriptTag.objects.get(pk=3) in version.tags.all():
                return version

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["round1"] = models.WorldCup.objects.filter(round=1).order_by("pk")
        context["round2"] = models.WorldCup.objects.filter(round=2).order_by("pk")
        context["round3"] = models.WorldCup.objects.filter(round=3).order_by("pk")
        context["round4"] = models.WorldCup.objects.filter(round=4).order_by("pk")
        context["round5"] = models.WorldCup.objects.filter(round=5).order_by("pk")
        context["round6"] = models.WorldCup.objects.filter(round=6).order_by("pk")
        context["round7"] = models.WorldCup.objects.filter(round=7).order_by("pk")

        return context


class WorldCupStatisticsView(generic.TemplateView):
    template_name = "worldcup/statistics.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        stats_character = None
        characters_to_display = 5

        queryset = models.ScriptVersion.objects.filter(tags=6)

        if "num" in self.request.GET:
            try:
                int(self.request.GET.get("num"))
                if int(self.request.GET.get("num")):
                    characters_to_display = int(self.request.GET.get("num"))
                    if characters_to_display < 1:
                        characters_to_display = 5
            except ValueError:
                pass

        context["total"] = queryset.count()

        character_count = {}
        character_count["additions"] = {}
        character_count["deletions"] = {}
        for type in models.CharacterType:
            character_count["additions"][type.value] = Counter()
            character_count["deletions"][type.value] = Counter()
            for character in models.Character.objects.all():
                if character.character_type != type:
                    continue
                character_count["additions"][character.character_type][character] = 0
                character_count["deletions"][character.character_type][character] = 0

        for round_of_32 in queryset:
            round_of_64 = round_of_32.script.versions.get(tags=5)
            additions = views.get_json_additions(
                round_of_32.content.copy(), round_of_64.content.copy()
            )
            for addition in additions:
                if addition.get("id", "_meta") == "_meta":
                    pass
                try:
                    character = models.Character.objects.get(
                        character_id=addition.get("id")
                    )
                except models.Character.DoesNotExist:
                    continue

                character_count["additions"][character.character_type][character] = (
                    character_count["additions"][character.character_type][character]
                    + 1
                )
            deletions = views.get_json_additions(
                round_of_64.content.copy(), round_of_32.content.copy()
            )
            for deletion in deletions:
                if deletion.get("id", "_meta") == "_meta":
                    pass
                try:
                    character = models.Character.objects.get(
                        character_id=deletion.get("id")
                    )
                except models.Character.DoesNotExist:
                    continue

                character_count["deletions"][character.character_type][character] = (
                    character_count["deletions"][character.character_type][character]
                    + 1
                )

        for type in models.CharacterType:
            context[type.value + "addition"] = character_count["additions"][
                type.value
            ].most_common(characters_to_display)
            context[type.value + "deletion"] = character_count["deletions"][
                type.value
            ].most_common(characters_to_display)

        return context
