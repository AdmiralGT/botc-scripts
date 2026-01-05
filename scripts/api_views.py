from rest_framework.views import APIView
from rest_framework.response import Response
from scripts import models
from collections import Counter
from drf_spectacular.utils import extend_schema


@extend_schema(
    responses={
        200: {
            "type": "object",
            "additionalProperties": {"type": "integer"},
            "description": "Character statistics with total count and individual character counts",
        }
    },
    summary="Get character statistics",
    description="Returns statistics for all characters including total count",
)
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
                        character = models.ClocktowerCharacter.objects.get(character_id=character)
                        queryset = queryset.filter(content__contains=[{"id": character.character_id}])
                    except models.ClocktowerCharacter.DoesNotExist:
                        continue
            elif param[0] == "character_or":
                orig_queryset = queryset.all()
                queryset = models.ScriptVersion.objects.none()
                for character in param[1]:
                    try:
                        character = models.ClocktowerCharacter.objects.get(character_id=character)
                        queryset = queryset | orig_queryset.filter(content__contains=[{"id": character.character_id}])
                    except models.ClocktowerCharacter.DoesNotExist:
                        continue
            elif param[0] == "exclude":
                for character in param[1]:
                    try:
                        character = models.ClocktowerCharacter.objects.get(character_id=character)
                        queryset = queryset.exclude(content__contains=[{"id": character.character_id}])
                    except models.ClocktowerCharacter.DoesNotExist:
                        continue

        for character in models.ClocktowerCharacter.objects.all():
            counter[character.character_id] = queryset.filter(
                content__contains=[{"id": character.character_id}]
            ).count()
        data = {}
        if "total" in request.query_params:
            data["total"] = queryset.count()
        for character in counter.most_common():
            data[character[0]] = character[1]
        return Response(data)


@extend_schema(
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "team": {"type": "string"},
                    "edition": {"type": "integer"},
                    "character_type": {"type": "string"},
                },
            },
            "description": "List of all clocktower characters",
        }
    },
    summary="Get all clocktower characters",
    description="Returns all official Blood on the Clocktower characters",
)
class CharactersAPI(APIView):
    permission_classes = []

    def get(self, request, format=None):
        data = []
        for character in models.ClocktowerCharacter.objects.all():
            data.append({
                "id": character.character_id,
                "name": character.character_name,
                "team": character.character_type.lower(),
                "edition": character.edition,
                "character_type": character.character_type,
            })
        return Response(data)
