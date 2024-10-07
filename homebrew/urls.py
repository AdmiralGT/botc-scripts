from django.urls import path
from scripts import views as s_views
from homebrew import views as h_views

# Routers provide an easy way of automatically determining the URL conf.
urlpatterns = [
    path("", h_views.ScriptsListView.as_view()),
    path("comment/<int:pk>/edit", s_views.CommentEditView.as_view(), name="edit_comment"),
    path("comment/new", s_views.CommentCreateView.as_view(), name="create_comment"),
    path("script/<int:pk>", s_views.ScriptView.as_view(), name="script"),
    path(
        "script/<int:pk>/<str:version>/similar",
        s_views.get_similar_scripts,
        name="similar",
    ),
    path("script/<int:pk>/<str:version>", s_views.ScriptView.as_view(), name="script"),
    path("script/<int:pk>/<str:version>/vote", s_views.vote_for_script, name="vote"),
    path(
        "script/<int:pk>/<str:version>/favourite",
        s_views.favourite_script,
        name="favourite",
    ),
    path(
        "script/<int:pk>/<str:version>/delete",
        s_views.ScriptDeleteView.as_view(),
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
    path("script/search", s_views.AdvancedSearchView.as_view(), name="advanced_search"),
    path("script/search/results", s_views.AdvancedSearchResultsView.as_view()),
    path("script/upload", s_views.ScriptUploadView.as_view(), name="upload"),
]