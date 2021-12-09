from rest_framework import serializers

from scripts.models import ScriptVersion


# Serializers define the API representation.
class ScriptSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="script.name")
    score = serializers.ReadOnlyField(source="votes.count")

    class Meta:
        model = ScriptVersion
        fields = ["pk", "name", "version", "content", "score"]
