from django.urls import include, path, re_path
from rest_framework import routers
from allauth.account.views import login, logout
from allauth.socialaccount import providers
from importlib import import_module
from scripts import views, viewsets, worldcup

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
    path("statistics/<str:character>", views.StatisticsView.as_view()),
    path("statistics/tags/<int:tags>", views.StatisticsView.as_view()),
    path("upload", views.ScriptUploadView.as_view(), name="upload"),
    path("account/social/", include("allauth.socialaccount.urls")),
    path("account/delete/", views.UserDeleteView.as_view(), name="delete_user"),
    path("account/scripts/", views.UserScriptsListView.as_view()),
    path("worldcup", worldcup.WorldCupView.as_view()),
    re_path(r"^login/$", login, name="account_login"),
    re_path(r"^logout/$", logout, name="account_logout"),
    re_path(r"^signup/$", login, name="account_signup"),
]

provider_urlpatterns = []
for provider in providers.registry.get_list():
    try:
        prov_mod = import_module(provider.get_package() + ".urls")
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
    if prov_urlpatterns:
        provider_urlpatterns += prov_urlpatterns
urlpatterns += provider_urlpatterns
