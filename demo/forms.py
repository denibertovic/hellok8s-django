from django import forms
from django_pixbin.forms import PixbinImageField, PixbinImageUploadWidget

from .models import Image

INPUT_CLASS = (
    "w-full px-4 py-2 bg-gray-700 bg-opacity-50 border border-gray-600 rounded-lg "
    "text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
)


class DirectUploadForm(forms.Form):
    """Browser-to-S3 upload, then a server-side check that the image exists."""

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Image title"}
        ),
    )
    image = PixbinImageField(
        verify_exists=True,
        widget=PixbinImageUploadWidget(),
        help_text="Drag and drop or click to upload directly to Pixbin via S3",
    )


class ImageEditForm(forms.ModelForm):
    """The model field supplies PixbinImageField with PixbinImageWidget on its own."""

    class Meta:
        model = Image
        fields = ("title", "image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASS
