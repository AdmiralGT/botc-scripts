from .models import ScriptVersion
from rest_framework import serializers

# Serializers define the API representation.
class ScriptSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source="script.name")
    score = serializers.ReadOnlyField(source="votes.count")

    class Meta:
        model = ScriptVersion
        fields = ["pk", "name", "version", "content", "score"]
