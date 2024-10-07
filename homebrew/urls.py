from django.urls import path
from scripts import views

# Routers provide an easy way of automatically determining the URL conf.
urlpatterns = [
    path("", views.ScriptsListView.as_view()),
    path("comment/<int:pk>/edit", views.CommentEditView.as_view(), name="edit_comment"),
    path("comment/new", views.CommentCreateView.as_view(), name="create_comment"),
    path("script/<int:pk>", views.ScriptView.as_view(), name="script"),
    path(
        "script/<int:pk>/<str:version>/similar",
        views.get_similar_scripts,
        name="similar",
    ),
    path("script/<int:pk>/<str:version>", views.ScriptView.as_view(), name="script"),
    path("script/<int:pk>/<str:version>/vote", views.vote_for_script, name="vote"),
    path(
        "script/<int:pk>/<str:version>/favourite",
        views.favourite_script,
        name="favourite",
    ),
    path(
        "script/<int:pk>/<str:version>/delete",
        views.ScriptDeleteView.as_view(),
        name="delete_script",
    ),
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
    path("script/search", views.AdvancedSearchView.as_view(), name="advanced_search"),
    path("script/search/results", views.AdvancedSearchResultsView.as_view()),
    path("script/upload", views.ScriptUploadView.as_view(), name="upload"),
]