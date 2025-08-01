from rest_framework import filters, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from scripts import models, serializers
from scripts import filters as filtersets
from scripts.views import translate_json_content
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404

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
    
    def create(self, request, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializers.ScriptUploadSerializer(*args, **kwargs)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_201_CREATED)

    # @authentication_classes([BasicAuthentication])
    # @permission_classes([ScriptApiPermissions])
    def update(self, request, *args, **kwargs):
        pass

    # @authentication_classes([BasicAuthentication])
    # @permission_classes([ScriptApiPermissions])
    def destroy(self, request, *args, **kwargs):
        pass


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

    schema = AutoSchema()

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
