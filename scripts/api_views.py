from collections import Counter

from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from scripts import models


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
        # plain_objects, not objects: this endpoint only ever counts, so the default manager's
        # vote/favourite annotations are joins and a GROUP BY for data that is never read.
        if "all" in request.query_params:
            queryset = models.ScriptVersion.plain_objects.all()
        else:
            queryset = models.ScriptVersion.plain_objects.filter(latest=True)
        queryset = queryset.filter(homebrewiness=models.Homebrewiness.CLOCKTOWER)

        for name, values in request.query_params.lists():
            if name not in ("character", "character_or", "exclude"):
                continue
            # Unknown character IDs are silently dropped rather than matching nothing.
            character_ids = list(
                models.ClocktowerCharacter.objects.filter(character_id__in=values).values_list(
                    "character_id", flat=True
                )
            )
            if not character_ids:
                continue
            if name == "character":
                for character_id in character_ids:
                    queryset = queryset.filter(characters__character_id=character_id)
            elif name == "character_or":
                queryset = queryset.filter(characters__character_id__in=character_ids).distinct()
            elif name == "exclude":
                for character_id in character_ids:
                    queryset = queryset.exclude(characters__character_id=character_id)

        # Seed every character to 0 so characters absent from the filtered scripts are still
        # reported, then overlay the counts from a single aggregate query.
        for character in models.ClocktowerCharacter.objects.all():
            counter[character.character_id] = 0

        character_counts = (
            models.ScriptVersionCharacter.objects.filter(script_version__in=queryset, character_id__in=list(counter))
            .values("character_id")
            .annotate(script_count=Count("script_version"))
        )
        for row in character_counts:
            counter[row["character_id"]] = row["script_count"]
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
            data.append(
                {
                    "id": character.character_id,
                    "name": character.character_name,
                    "edition": character.edition,
                    "character_type": character.character_type,
                }
            )
        return Response(data)
