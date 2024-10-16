from rest_framework import filters, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from homebrew import models, serializers
from homebrew import filters as filtersets

class HomebrewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.HomebrewVersion.objects.all()
    serializer_class = serializers.HomebrewSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = filtersets.HomebrewVersionFilter
    ordering_fields = ["pk", "score"]
    ordering = ["-pk"]

    def get_queryset(self):
        queryset = models.HomebrewVersion.objects.all()
        latest = self.request.query_params.get("latest")
        if latest:
            queryset = models.HomebrewVersion.objects.filter(latest=True)
        return queryset

    @action(methods=["get"], detail=True)
    def json(self, _, pk=None):
        return Response(models.HomebrewVersion.objects.get(pk=pk).content)


