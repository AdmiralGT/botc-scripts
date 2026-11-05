from django.core.management.base import BaseCommand
from django.db.models import Count, OuterRef, PositiveIntegerField, Subquery
from django.db.models.functions import Coalesce

from scripts.models import Comment, Favourite, Script, Vote

BATCH_SIZE = 500


class Command(BaseCommand):
    help = "Recalculate the stored vote, favourite and comment counts on every script"

    def handle(self, *args, **options):
        total = Script.objects.count()
        self.stdout.write(f"Recalculating counts for {total} scripts...")
        maximum_pk = Script.objects.order_by("-pk").values_list("pk", flat=True).first()

        vote_count = (
            Vote.objects.filter(parent=OuterRef("pk"))
            .order_by()
            .values("parent")
            .annotate(count=Count("pk"))
            .values("count")
        )
        favourite_count = (
            Favourite.objects.filter(parent=OuterRef("pk"))
            .order_by()
            .values("parent")
            .annotate(count=Count("pk"))
            .values("count")
        )
        comment_count = (
            Comment.objects.filter(script=OuterRef("pk"))
            .order_by()
            .values("script")
            .annotate(count=Count("pk"))
            .values("count")
        )

        processed = 0
        last_pk = 0
        while maximum_pk is not None:
            script_pks = list(
                Script.objects.filter(pk__gt=last_pk, pk__lte=maximum_pk)
                .order_by("pk")
                .values_list("pk", flat=True)[:BATCH_SIZE]
            )
            if not script_pks:
                break

            scripts = Script.objects.filter(pk__in=script_pks)
            scripts.update(num_votes=Coalesce(Subquery(vote_count, output_field=PositiveIntegerField()), 0))
            scripts.update(num_favourites=Coalesce(Subquery(favourite_count, output_field=PositiveIntegerField()), 0))
            scripts.update(num_comments=Coalesce(Subquery(comment_count, output_field=PositiveIntegerField()), 0))

            processed += len(script_pks)
            last_pk = script_pks[-1]
            self.stdout.write(f"Progress: {processed}/{total}")

        self.stdout.write(self.style.SUCCESS(f"Successfully recalculated counts for {processed} scripts"))
