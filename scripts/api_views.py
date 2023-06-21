from rest_framework.views import APIView
from rest_framework.response import Response
from scripts import models
from collections import Counter


class StatisticsAPI(APIView):
    permission_classes = []

    def get(self, request, format=None):
        counter = Counter()
        if "all" in request.query_params:
            queryset = models.ScriptVersion.objects.all()
        else:
            queryset = models.ScriptVersion.objects.filter(latest=True)

        for param in request.query_params.lists():
            if param[0] == "character":
                for character in param[1]:
                    try:
                        character = models.Character.objects.get(character_id=character)
                        queryset = queryset.filter(
                            content__contains=[{"id": character.character_id}]
                        )
                    except models.Character.DoesNotExist:
                        continue
            elif param[0] == "character_or":
                orig_queryset = queryset.all()
                queryset = models.ScriptVersion.objects.none()
                for character in param[1]:
                    try:
                        character = models.Character.objects.get(character_id=character)
                        queryset = queryset | orig_queryset.filter(
                            content__contains=[{"id": character.character_id}]
                        )
                    except models.Character.DoesNotExist:
                        continue
            elif param[0] == "exclude":
                for character in param[1]:
                    try:
                        character = models.Character.objects.get(character_id=character)
                        queryset = queryset.exclude(
                            content__contains=[{"id": character.character_id}]
                        )
                    except models.Character.DoesNotExist:
                        continue

        for character in models.Character.objects.all():
            counter[character.character_id] = queryset.filter(
                content__contains=[{"id": character.character_id}]
            ).count()
        data = {}
        if "total" in request.query_params:
            data["total"] = queryset.count()
        for character in counter.most_common():
            data[character[0]] = character[1]
        return Response(data)
