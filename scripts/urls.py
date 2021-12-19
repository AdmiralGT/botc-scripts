from django.urls import include, path, re_path
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LogoutView
from rest_framework import routers

from scripts import views, viewsets

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"scripts", viewsets.ScriptViewSet)

urlpatterns = [
    path("", views.ScriptsListView.as_view()),
    path("api/", include(router.urls)),
    path("script/<int:pk>", views.ScriptView.as_view(), name="script"),
    path("script/<int:pk>/vote", views.vote_for_script, name="vote"),
    path("script/<int:pk>/<str:version>", views.ScriptView.as_view(), name="script"),
    path(
        "script/<int:pk>/<str:version>/download",
        views.download_json,
        name="download_json",
    ),
    path(
        "script/<int:pk>/<str:version>/download_pdf",
        views.download_pdf,
        name="download_pdf",
    ),
    path("statistics", views.StatisticsView.as_view()),
    path("upload", views.ScriptUploadView.as_view(), name="upload"),
    path("accounts/", include("allauth.urls")),
]
