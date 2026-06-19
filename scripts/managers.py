from django.db import models


class ScriptViewManager(models.Manager):
    def get_queryset(self):
        qs = (
            super(ScriptViewManager, self)
            .get_queryset()
            .annotate(
                score=models.Count("script__votes", distinct=True),
                num_favs=models.Count("script__favourites", distinct=True),
            )
        )
        return qs


class CollectionManager(models.Manager):
    def get_queryset(self):
        qs = super(CollectionManager, self).get_queryset().annotate(scripts_in_collection=models.Count("scripts"))
        return qs
