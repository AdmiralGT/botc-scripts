from rest_framework import filters, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework import status
from scripts import models, serializers, script_json
from scripts import filters as filtersets
from scripts.views import (
    translate_json_content,
    create_characters_and_determine_homebrew_status,
    count_character,
    calculate_edition,
)
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from versionfield import Version


class ScriptApiPermissions(BasePermission):
    """
    Custom permission to only allow authenticated users to create, update, or delete scripts.
    All users can read scripts.
    """

    def has_permission(self, request, view):
        if request.user and request.user.has_perm("scripts.api_write_permission"):
            return True
        return False


class ScriptViewSet(viewsets.ModelViewSet):
    queryset = models.ScriptVersion.objects.all()
    serializer_class = serializers.ScriptSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = filtersets.ScriptVersionFilter
    ordering_fields = ["pk", "score"]
    ordering = ["-pk"]

    def get_queryset(self):
        queryset = models.ScriptVersion.objects.all()
        latest = self.request.query_params.get("latest")
        if latest:
            queryset = models.ScriptVersion.objects.filter(latest=True)
        return queryset

    @action(methods=["get"], detail=True)
    def json(self, _, pk=None):
        return Response(models.ScriptVersion.objects.get(pk=pk).content)

    @authentication_classes([BasicAuthentication])
    @permission_classes([IsAuthenticated, ScriptApiPermissions])
    def create(self, request, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        serializer = serializers.ScriptUploadSerializer(data=request.data, *args, **kwargs)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_createable(raise_exception=True):
            return Response(
                {"error": "A script with this name and version already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        is_latest = True
        current_tags = None

        # Either get the current script, or create a new one based on the name.
        script, created = models.Script.objects.get_or_create(name=serializer.validated_data.get("name"))
        user = request.user if request.user.is_authenticated else None
        if created:
            script.owner = user
            script.save()
        else:
            if script.owner and script.owner != user:
                return Response(
                    {"error": "You do not have permission to update this script."}, status=status.HTTP_403_FORBIDDEN
                )
            if script.latest_version():
                # We need to protect this code against instances where a script doesn't
                # have a latest version.
                if Version(serializer.validated_data.get("version")) > script.latest_version().version:
                    # This is newer than the latest version, so set that
                    # version to not be latest.
                    current_tags = script.latest_version().tags
                    latest_version = script.latest_version()
                    latest_version.latest = False
                    latest_version.save()
                else:
                    # We're uploading an older version than the latest, so don't mark this version
                    # as the latest, that's still the current latest.
                    is_latest = False

        json = script_json.get_json_content(serializer.validated_data)
        homebrewiness = create_characters_and_determine_homebrew_status(json, script)

        num_townsfolk = count_character(json, models.CharacterType.TOWNSFOLK)
        num_outsiders = count_character(json, models.CharacterType.OUTSIDER)
        num_minions = count_character(json, models.CharacterType.MINION)
        num_demons = count_character(json, models.CharacterType.DEMON)
        num_fabled = count_character(json, models.CharacterType.FABLED)
        num_travellers = count_character(json, models.CharacterType.TRAVELLER)
        edition = calculate_edition(json)

        # Create the Script Version object from the form.
        self.script_version = models.ScriptVersion.objects.create(
            version=serializer.validated_data.get("version"),
            script_type=serializer.validated_data.get("script_type"),
            content=json,
            script=script,
            pdf=serializer.validated_data.get("pdf") or None,
            author=serializer.validated_data.get("author") or None,
            latest=is_latest,
            num_townsfolk=num_townsfolk,
            num_outsiders=num_outsiders,
            num_minions=num_minions,
            num_demons=num_demons,
            num_fabled=num_fabled,
            num_travellers=num_travellers,
            edition=edition,
            homebrewiness=homebrewiness,
        )
        if serializer.validated_data.get("notes", None):
            self.script_version.notes = serializer.validated_data.get("notes")
            self.script_version.save()

        # Re-add public tags that are inheritable and haven't been included
        if current_tags:
            self.script_version.tags.add(*current_tags.all())

        if homebrewiness == models.Homebrewiness.HYBRID:
            try:
                hybrid_tag = models.ScriptTag.objects.get(name="Hybrid Script")
                self.script_version.tags.add(hybrid_tag)
            except models.ScriptTag.DoesNotExist:
                pass
        elif homebrewiness == models.Homebrewiness.HOMEBREW:
            try:
                homebrew_tag = models.ScriptTag.objects.get(name="Homebrew Script")
                self.script_version.tags.add(homebrew_tag)
            except models.ScriptTag.DoesNotExist:
                pass

        return Response(status=status.HTTP_201_CREATED, data={"pk": self.script_version.pk})

    @authentication_classes([BasicAuthentication])
    @permission_classes([IsAuthenticated, ScriptApiPermissions])
    def update(self, request, *args, **kwargs):
        pk = kwargs.pop("pk")
        try:
            instance = models.ScriptVersion.objects.get(pk=pk)
        except models.ScriptVersion.DoesNotExist:
            return Response({"error": "Script version not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ScriptUploadSerializer(data=request.data, *args, **kwargs)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_expected_script(instance, raise_exception=True):
            return Response(
                {"error": "You cannot change the name or version of an existing script."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if instance.script.owner and instance.script.owner != request.user:
            return Response(
                {"error": "You do not have permission to update this script."}, status=status.HTTP_403_FORBIDDEN
            )

        if serializer.validated_data.get("content", None):
            json = script_json.get_json_content(serializer.validated_data)

            if instance.content != json:
                return Response(
                    {"error": "You cannot modify the content of an existing script."}, status=status.HTTP_403_FORBIDDEN
                )

        if serializer.validated_data.get("author", None):
            instance.author = serializer.validated_data.get("author")
            instance.save()
        if serializer.validated_data.get("pdf", None):
            instance.pdf = serializer.validated_data.get("pdf")
            instance.save()
        if serializer.validated_data.get("notes", None):
            instance.notes = serializer.validated_data.get("notes")
            instance.save()

        return Response(status=status.HTTP_200_OK)

    @authentication_classes([BasicAuthentication])
    @permission_classes([IsAuthenticated, ScriptApiPermissions])
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            instance = models.ScriptVersion.objects.get(pk=pk)
        except models.ScriptVersion.DoesNotExist:
            return Response({"error": "Script version not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.script.owner != self.request.user:
            return Response(
                {"error": "You do not have permission to delete this script."}, status=status.HTTP_403_FORBIDDEN
            )

        script = instance.script
        instance.delete()

        if script.versions.count() > 0:
            latest_version = script.latest_version()
            latest_version.latest = True
            latest_version.save()
        else:
            script.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TranslateScriptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ScriptVersion.objects.all()
    serializer_class = serializers.ScriptSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = filtersets.ScriptVersionFilter
    ordering_fields = ["pk", "score"]
    ordering = ["-pk"]

    def get_queryset(self):
        queryset = models.ScriptVersion.objects.all()
        latest = self.request.query_params.get("latest")
        if latest:
            queryset = models.ScriptVersion.objects.filter(latest=True)
        return queryset

    def get_object(self, pk: int):
        try:
            return models.ScriptVersion.objects.get(pk=pk)
        except models.ScriptVersion.DoesNotExist:
            raise Http404

    def retrieve(self, request: Request, script_version: int, language: str):
        if language not in models.Translation.objects.values_list("language", flat=True).distinct("language").order_by(
            "language"
        ):
            return Response(
                {"error": "Invalid language specified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_object(script_version)
        translated_content = translate_json_content(instance.content, language)
        return Response(translated_content)


class TranslationViewSet(viewsets.ModelViewSet):
    queryset = models.Translation.objects.all()
    serializer_class = serializers.TranslationSerializer

    def get_object(self, language: str, character: str):
        return models.Translation.objects.get(language=language, character_id=character)

    def retrieve(self, request: Request, language: str, character_id: str):
        instance = self.get_object(language, character_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request: Request, language: str, character_id: str, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object(language, character_id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request: Request, language: str, character_id: str, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(language=language, character_id=character_id)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
