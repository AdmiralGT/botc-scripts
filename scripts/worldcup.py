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
        script = models.Script.objects.get(pk=52)
        self.get_world_cup_script(models.Script.objects.get(pk=52))
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=52)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=196)),
                "vod": "https://forms.gle/5cQWem19C5v56pfA7",
                "form": "https://forms.gle/5cQWem19C5v56pfA7",
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=208)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=216)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=165)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=200)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=167)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=218)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=217)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=197)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=211)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=191)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=213)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=195)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=206)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=194)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=166)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=205)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=109)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=186)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=177)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=185)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=189)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=183)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=72)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=203)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=171)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=179)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=172)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=187)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=192)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=210)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=223)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=212)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=184)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=168)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=214)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=174)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=173)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=181)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=87)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=198)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=215)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=62)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=193)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=190)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=199)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=140)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=69)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=209)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=176)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=122)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=169)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=182)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=178)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=170)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=175)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=202)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=180)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=180)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=207)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=188)),
            }
        )
        round1.append(
            {
                "script1": self.get_world_cup_script(models.Script.objects.get(pk=66)),
                "script2": self.get_world_cup_script(models.Script.objects.get(pk=201)),
            }
        )
        context["round1"] = round1
        return context
