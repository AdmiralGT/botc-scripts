from django.db import models


class ScriptViewManager(models.Manager):
    def get_queryset(self):
        # Counts are stored on Script and maintained by the interaction signals.
        return (
            super()
            .get_queryset()
            .annotate(
                score=models.F("script__num_votes"),
                num_favs=models.F("script__num_favourites"),
                num_comments=models.F("script__num_comments"),
            )
        )


class CollectionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(scripts_in_collection=models.Count("scripts"))
