from django.db.models import F, Max, QuerySet
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from scripts import models
from scripts.character_mask import MASK_BITS, build_mask
from scripts.models import CORE_CHARACTER_TYPES


def _is_script_deletion(origin):
    return isinstance(origin, models.Script) or (isinstance(origin, QuerySet) and origin.model is models.Script)


@receiver(post_save, sender=models.Comment)
def update_comment_count_on_create(sender, instance, created, **kwargs):
    if created and instance.script_id is not None:
        models.Script.objects.filter(pk=instance.script_id).update(num_comments=F("num_comments") + 1)


@receiver(post_delete, sender=models.Comment)
def update_comment_count_on_delete(sender, instance, origin=None, **kwargs):
    if not _is_script_deletion(origin) and instance.script_id is not None:
        models.Script.objects.filter(pk=instance.script_id).update(num_comments=F("num_comments") - 1)


@receiver(post_save, sender=models.Vote)
def update_vote_count_on_create(sender, instance, created, **kwargs):
    if created and instance.parent_id is not None:
        models.Script.objects.filter(pk=instance.parent_id).update(num_votes=F("num_votes") + 1)


@receiver(post_delete, sender=models.Vote)
def update_vote_count_on_delete(sender, instance, origin=None, **kwargs):
    if not _is_script_deletion(origin) and instance.parent_id is not None:
        models.Script.objects.filter(pk=instance.parent_id).update(num_votes=F("num_votes") - 1)


@receiver(post_save, sender=models.Favourite)
def update_favourite_count_on_create(sender, instance, created, **kwargs):
    if created and instance.parent_id is not None:
        models.Script.objects.filter(pk=instance.parent_id).update(num_favourites=F("num_favourites") + 1)


@receiver(post_delete, sender=models.Favourite)
def update_favourite_count_on_delete(sender, instance, origin=None, **kwargs):
    if not _is_script_deletion(origin) and instance.parent_id is not None:
        models.Script.objects.filter(pk=instance.parent_id).update(num_favourites=F("num_favourites") - 1)


@receiver(pre_save, sender=models.ClocktowerCharacter)
def assign_bit_index(sender, instance, **kwargs):
    if instance.bit_index is not None:
        return
    existing = sender.objects.filter(pk=instance.pk).values_list("bit_index", flat=True).first()
    if existing is not None:
        instance.bit_index = existing
        return
    highest = sender.objects.aggregate(highest=Max("bit_index"))["highest"]
    instance.bit_index = 0 if highest is None else highest + 1
    if instance.bit_index >= MASK_BITS:
        raise ValueError(f"Character mask is full ({MASK_BITS} bits)")
    instance._bit_index_assigned = True


@receiver(post_save, sender=models.ClocktowerCharacter)
def update_masks_for_new_character(sender, instance, **kwargs):
    if not getattr(instance, "_bit_index_assigned", False) or instance.character_type not in CORE_CHARACTER_TYPES:
        return
    bit_map = sender.character_bit_index_mapping()
    versions = list(
        models.ScriptVersion.plain_objects.filter(content__contains=[{"id": instance.character_id}]).only("content")
    )
    for version in versions:
        version.character_mask = build_mask(version.content, bit_map)
    models.ScriptVersion.plain_objects.bulk_update(versions, ["character_mask"], batch_size=500)
