from django.db import models
from django.db.models.functions import Coalesce

class ScriptViewManager(models.Manager):

    def get_queryset(self):
        qs = super(ScriptViewManager, self).get_queryset().annotate(score=Coalesce(models.Count("votes"), 0))
        return qs