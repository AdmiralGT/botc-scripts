from django.views import generic
from scripts import models
from typing import Dict, Any


class WorldCupView(generic.TemplateView):
    template_name = "worldcup.html"

    def get_world_cup_script(self, script: models.Script):
        for version in script.versions.all():
            if models.ScriptTag.objects.get(pk=3) in version.tags.all():
                return version

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        round1 = []
        context["round1"] = models.WorldCup.objects.filter(round=1).order_by("pk")
        context["round2"] = models.WorldCup.objects.filter(round=2).order_by("pk")

        return context
