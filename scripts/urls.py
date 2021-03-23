from django.urls import path
from . import views

urlpatterns = [
    path("", views.ScriptsListView.as_view()),
    path("script/<int:pk>", views.ScriptView.as_view(), name="script"),
    path("script/<int:pk>/<str:version>", views.ScriptView.as_view(), name="script"),
    path(
        "script/<int:pk>/<str:version>/download", views.download_json, name="download_json"
    ),
    path(
        "script/<int:pk>/<str:version>/download_pdf", views.download_pdf, name="download_pdf"
    ),
    path("upload", views.ScriptUploadView.as_view()),
]
