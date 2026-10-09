from django.urls import path

from . import views

app_name = "demo"

urlpatterns = [
    path("pixbin/", views.pixbin_landing, name="pixbin_landing"),
    path("pixbin/upload/", views.pixbin_upload, name="pixbin_upload"),
    path("pixbin/forms/", views.pixbin_forms, name="pixbin_forms"),
    path("pixbin/sdk/", views.pixbin_sdk, name="pixbin_sdk"),
    path(
        "pixbin/download/<uuid:image_id>/",
        views.pixbin_download,
        name="pixbin_download",
    ),
]
