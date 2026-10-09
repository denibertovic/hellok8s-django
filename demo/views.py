import io

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_pixbin import get_pixbin_client
from PIL import Image as PILImage
from PIL import UnidentifiedImageError
from pixbin import PixbinError, crop_square, optimize_web, thumbnail

from .forms import DirectUploadForm, ImageEditForm
from .models import Image


def pixbin_landing(request):
    """Landing page with overview and links to feature pages."""
    return render(request, "demo/pixbin/landing.html")


@login_required
def pixbin_upload(request):
    """Template tags, filters, and transformations showcase."""
    user_images = Image.objects.filter(uploaded_by=request.user)

    context = {
        "images": user_images,
        "selected_image": None,
    }

    # Handle image selection
    image_id = request.GET.get("image")
    if image_id:
        selected = get_object_or_404(Image, id=image_id, uploaded_by=request.user)
        context["selected_image"] = selected
        context["helper_method_url"] = selected.get_image_url("resize:300x300:fit")

    # Handle delete (called via fetch DELETE from JS)
    if request.method == "DELETE" and image_id:
        image = get_object_or_404(Image, id=image_id, uploaded_by=request.user)
        try:
            client = get_pixbin_client()
            client.delete(str(image.image))
        except (PixbinError, requests.RequestException) as e:
            return JsonResponse({"error": f"Pixbin delete failed: {e}"}, status=500)
        image.delete()
        return JsonResponse({"status": "success"})

    # Handle new upload
    if request.method == "POST" and request.FILES.get("image"):
        try:
            client = get_pixbin_client()
            uploaded_file = request.FILES["image"]
            title = request.POST.get("title", uploaded_file.name)

            # Do not wait for variant processing, so the page renders while
            # Pixbin is still working and pixbin.js gets to show its shimmer.
            pixbin_id = client.upload_file(uploaded_file, max_wait=0)

            image = Image.objects.create(
                title=title,
                image=pixbin_id,
                original_filename=uploaded_file.name,
                uploaded_by=request.user,
            )

            messages.success(request, "Image uploaded successfully!")
            return redirect(f"{request.path}?image={image.id}")

        except (PixbinError, requests.RequestException) as e:
            messages.error(request, f"Upload failed: {e}")

    return render(request, "demo/pixbin/upload.html", context)


@login_required
def pixbin_forms(request):
    """Form fields and widgets showcase."""
    user_images = Image.objects.filter(uploaded_by=request.user)

    edit_image = None
    if request.GET.get("image"):
        edit_image = get_object_or_404(
            Image, id=request.GET["image"], uploaded_by=request.user
        )
    elif user_images.exists():
        edit_image = user_images.first()

    upload_form = DirectUploadForm()
    edit_form = ImageEditForm(instance=edit_image) if edit_image else None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "upload":
            upload_form = DirectUploadForm(request.POST)
            if upload_form.is_valid():
                image = Image.objects.create(
                    title=upload_form.cleaned_data["title"],
                    image=upload_form.cleaned_data["image"],
                    uploaded_by=request.user,
                )
                messages.success(
                    request, f"Saved '{image.title}' with Pixbin ID {image.image}"
                )
                return redirect(f"{request.path}?image={image.id}")

        elif form_type == "edit" and edit_image:
            edit_form = ImageEditForm(request.POST, instance=edit_image)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, f"Updated '{edit_image.title}'")
                return redirect(f"{request.path}?image={edit_image.id}")

    return render(
        request,
        "demo/pixbin/forms.html",
        {
            "upload_form": upload_form,
            "edit_form": edit_form,
            "edit_image": edit_image,
            "images": user_images,
        },
    )


@login_required
def pixbin_sdk(request):
    """Python SDK features showcase."""
    user_images = Image.objects.filter(uploaded_by=request.user)
    sample_image = user_images.first()

    status_data = None
    status_error = None

    # Check status on request
    if sample_image and request.GET.get("check_status"):
        try:
            client = get_pixbin_client()
            status_data = client.get_status(str(sample_image.image))
        except (PixbinError, requests.RequestException) as e:
            status_error = str(e)

    helper_examples = {
        "thumbnail": thumbnail(300, 300),
        "crop_square": crop_square(200),
        "optimize_web": optimize_web(),
    }

    return render(
        request,
        "demo/pixbin/sdk.html",
        {
            "sample_image": sample_image,
            "status_data": status_data,
            "status_error": status_error,
            "helper_examples": helper_examples,
            "images": user_images,
        },
    )


def _image_response(image_bytes, filename_stem):
    """Build a download response with the content type sniffed from the bytes."""
    try:
        with PILImage.open(io.BytesIO(image_bytes)) as im:
            fmt = im.format
    except UnidentifiedImageError:
        fmt = None
    content_type = PILImage.MIME.get(fmt, "application/octet-stream")
    extension = (fmt or "bin").lower().replace("jpeg", "jpg")

    response = HttpResponse(image_bytes, content_type=content_type)
    response["Content-Disposition"] = (
        f'attachment; filename="{filename_stem}.{extension}"'
    )
    return response


@login_required
def pixbin_download(request, image_id):
    """Download transformed or original image bytes."""
    get_object_or_404(Image, image=image_id, uploaded_by=request.user)

    transform = request.GET.get("transform", "")
    download_type = request.GET.get("type", "transformed")

    try:
        client = get_pixbin_client()

        if download_type == "original" or not transform:
            image_bytes = client.download_original(str(image_id))
            filename_stem = f"{image_id}_original"
        else:
            image_bytes = client.download_transformed(str(image_id), transform)
            safe_transform = transform.replace(":", "_").replace(",", "_")
            filename_stem = f"{image_id}_{safe_transform}"

        return _image_response(image_bytes, filename_stem)

    except (PixbinError, requests.RequestException) as e:
        return JsonResponse({"error": str(e)}, status=500)
