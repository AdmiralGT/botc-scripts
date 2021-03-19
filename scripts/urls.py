from django.urls import path
from . import views

urlpatterns = [
    path("", views.ScriptsView.as_view(), name="index"),
    path("script/<int:pk>", views.ScriptView.as_view(), name="script"),
    path(
        "script/<int:pk>/<str:version>/download", views.download_json, name="download_json"
    ),
    path(
        "script/<int:pk>/<str:version>/download_pdf", views.download_pdf, name="download_pdf"
    ),
    path("upload", views.ScriptUploadView.as_view()),
    path("table", views.ScriptsListView.as_view())
]
