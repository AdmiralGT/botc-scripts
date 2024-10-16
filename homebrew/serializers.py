from rest_framework import serializers

from homebrew import models


class HomebrewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="homebrewscript.name")
    score = serializers.ReadOnlyField(source="votes.count")

    class Meta:
        model = models.HomebrewVersion
        fields = ["pk", "name", "version", "author", "content", "score"]
