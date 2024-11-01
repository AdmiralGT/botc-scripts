from rest_framework import filters, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from scripts import models, serializers
from scripts import filters as filtersets
from django_filters.rest_framework import DjangoFilterBackend


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ScriptVersion.objects.all()
    serializer_class = serializers.ScriptSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = filtersets.ScriptVersionFilter
    ordering_fields = ["pk", "score"]
    ordering = ["-pk"]

    def get_queryset(self):
        queryset = models.ScriptVersion.objects.all()
        latest = self.request.query_params.get("latest")
        if latest:
            queryset = models.ScriptVersion.objects.filter(latest=True)
        return queryset

    @action(methods=["get"], detail=True)
    def json(self, _, pk=None):
        return Response(models.ScriptVersion.objects.get(pk=pk).content)


class TranslationViewSet(viewsets.ModelViewSet):
    queryset = models.Translation.objects.all()
    serializer_class = serializers.TranslationSerializer

    schema = AutoSchema()

    def get_object(self, language: str, character: str):
        return models.Translation.objects.get(language=language, character_id=character)

    def retrieve(self, request: Request, language: str, character_id: str):
        instance = self.get_object(language, character_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request: Request, language: str, character_id: str, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object(language, character_id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request: Request, language: str, character_id: str, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(language=language, character_id=character_id)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
