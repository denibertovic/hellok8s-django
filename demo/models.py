from django.conf import settings
from django.db import models
from django_pixbin.fields import PixbinImageField


class Image(models.Model):
    """
    Demo model showcasing PixbinImageField usage.
    """

    title = models.CharField(max_length=200)
    image = PixbinImageField()
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demo_images",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # noqa: RUF012

    def __str__(self):
        return self.title
