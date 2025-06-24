from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path("<int:post_id>/<slug:slug>/", views.post_detail, name="detail"),
    path("<int:post_id>/", views.post_detail, name="detail-no-slug"),
]
