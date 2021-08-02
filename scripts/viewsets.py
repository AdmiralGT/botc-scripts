from rest_framework import filters, viewsets

from . import models, serializers


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ScriptVersion.objects.all()
    serializer_class = serializers.ScriptSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["pk", "score"]
    ordering = ["-pk"]
