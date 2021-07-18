from . import models, serializers
from rest_framework import filters, viewsets


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ScriptVersion.objects.all()
    serializer_class = serializers.ScriptSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["pk", "score"]
