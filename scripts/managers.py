from django.db import models


class ScriptViewManager(models.Manager):
    def get_queryset(self):
        qs = (
            super(ScriptViewManager, self)
            .get_queryset()
            .annotate(num_tags=models.Count("tags", distinct=True))
            .annotate(score=models.Count("votes", distinct=True))
            .annotate(num_favs=models.Count("favourites", distinct=True))
            .annotate(num_comments=models.Count("script__comments", distinct=True))
        )
        return qs


class CollectionManager(models.Manager):
    def get_queryset(self):
        qs = super(CollectionManager, self).get_queryset().annotate(scripts_in_collection=models.Count("scripts"))
        return qs
