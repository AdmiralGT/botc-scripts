from django.urls import path
from scripts import views as s_views
from homebrew import views as h_views

# Routers provide an easy way of automatically determining the URL conf.
urlpatterns = [
    path("", h_views.HomebrewListView.as_view()),
    path("comment/<int:pk>/edit", s_views.CommentEditView.as_view(), name="edit_comment"),
    path("comment/new", s_views.CommentCreateView.as_view(), name="create_comment"),
    path(
        "comment/<int:pk>/delete",
        s_views.CommentDeleteView.as_view(),
        name="delete_homebrew_comment",
    ),
    path("script/<int:pk>", h_views.HomebrewScriptView.as_view(), name="script"),
    path(
        "script/<int:pk>/<str:version>/similar",
        s_views.get_similar_scripts,
        name="similar",
    ),
    path("script/<int:pk>/<str:version>", h_views.HomebrewScriptView.as_view(), name="script"),
    path("script/<int:pk>/<str:version>/vote", s_views.vote_for_script, name="vote"),
    path(
        "script/<int:pk>/<str:version>/favourite",
        s_views.favourite_script,
        name="favourite",
    ),
    path(
        "script/<int:pk>/<str:version>/delete",
        h_views.HomebrewDeleteView.as_view(),
        name="delete_script",
    ),
    path(
        "script/<int:pk>/<str:version>/download",
        s_views.download_json,
        name="download_json",
    ),
    path(
        "script/<int:pk>/<str:version>/download_pdf",
        s_views.download_pdf,
        name="download_pdf",
    ),
    path("script/upload", s_views.ScriptUploadView.as_view(), name="upload"),
]