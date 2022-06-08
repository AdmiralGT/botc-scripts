from django.db import models
from django.db.models.functions import Coalesce


class ScriptViewManager(models.Manager):
    def get_queryset(self):
        qs = (
            super(ScriptViewManager, self)
            .get_queryset()
            .annotate(score=Coalesce(models.Count("votes"), 0))
            .annotate(num_favs=Coalesce(models.Count("favourites"), 0))
            .annotate(num_comments=Coalesce(models.Count("script__comments"), 0))
        )
        return qs


class CollectionManager(models.Manager):
    def get_queryset(self):
        qs = (
            super(CollectionManager, self)
            .get_queryset()
            .annotate(scripts_in_collection=models.Count("scripts"))
        )
        return qs
