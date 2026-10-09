from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", "image", "uploaded_by", "created_at")
    readonly_fields = ("created_at",)
