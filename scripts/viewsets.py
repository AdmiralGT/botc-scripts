from django.http import Http404
from rest_framework import filters, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from scripts import models, serializers


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ScriptVersion.objects.all()
    serializer_class = serializers.ScriptSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["pk", "score"]
    ordering = ["-pk"]

    @action(methods=["get"], detail=True)
    def json(self, request, pk=None):
        return Response(models.ScriptVersion.objects.get(pk=pk).content)


class TranslationViewSet(viewsets.ModelViewSet):
    queryset = models.Translation.objects.all()
    serializer_class = serializers.TranslationSerializer

    def get_object(self, language: str, character: str):
        return models.Translation.objects.get(language=language, character_id=character)

    # @action(
    #     detail=False,
    #     methods=["put", "get"],
    #     url_path="(?P<language>\\w+)/(?P<character_id>\\w+)",
    # )
    # def translation(self, request: Request, language: str, character_id: str):
    #     instance = self.get_object(language, character_id)
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

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
