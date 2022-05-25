from rest_framework import filters, viewsets
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
