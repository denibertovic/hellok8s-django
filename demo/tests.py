import uuid
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django_pixbin.client import get_pixbin_client
from pixbin import PixbinError

from .models import Image


@override_settings(PIXBIN_API_TOKEN="test-token", PIXBIN_BASE_URL="https://pixbin.test")
class PixbinDemoPagesTest(TestCase):
    def setUp(self):
        get_pixbin_client.cache_clear()
        self.user = get_user_model().objects.create_user(
            email="demo@example.com",
            first_name="Demo",
            last_name="User",
            password="password",
        )
        self.image = Image.objects.create(
            title="First", image=uuid.uuid4(), uploaded_by=self.user
        )
        self.client.force_login(self.user)

    def test_landing_is_public(self):
        self.client.logout()

        response = self.client.get(reverse("demo:pixbin_landing"))

        self.assertEqual(response.status_code, 200)

    def test_feature_pages_require_login(self):
        self.client.logout()

        for name in ("pixbin_upload", "pixbin_forms", "pixbin_sdk"):
            response = self.client.get(reverse(f"demo:{name}"))
            self.assertEqual(response.status_code, 302, name)

    def test_upload_page_renders_all_template_tags(self):
        response = self.client.get(
            reverse("demo:pixbin_upload"), {"image": self.image.id}
        )

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("/api/v1/image/", html)
        self.assertIn(f"/{self.image.image}", html)
        self.assertIn("srcset=", html)
        self.assertIn("window.PIXBIN_CONFIG", html)
        self.assertNotIn("pixbin_image ", html)

    def test_forms_page_renders_both_widgets(self):
        response = self.client.get(reverse("demo:pixbin_forms"))

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("pixbin-upload-widget", html)
        self.assertIn("data-pixbin-preview-widget", html)
        self.assertIn('data-check-endpoint="/pixbin/image/__IMAGE_ID__/exists/"', html)
        self.assertIn("django_pixbin/js/upload.js", html)

    def test_sdk_page_uses_helper_functions(self):
        response = self.client.get(reverse("demo:pixbin_sdk"))

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("resize:300x300:fit,quality:85", html)
        self.assertIn("crop:center,resize:200x200:exact", html)
        self.assertIn("resize:1920x1920:fit,quality:85,format:webp", html)

    def test_edit_form_updates_title(self):
        response = self.client.post(
            reverse("demo:pixbin_forms") + f"?image={self.image.id}",
            {"form_type": "edit", "title": "Renamed", "image": str(self.image.image)},
        )

        self.assertEqual(response.status_code, 302)
        self.image.refresh_from_db()
        self.assertEqual(self.image.title, "Renamed")

    @patch("django_pixbin.client.get_pixbin_client")
    def test_upload_form_verifies_and_saves(self, mock_get_client):
        client = Mock()
        client.get_status.return_value = {"processing_status": "completed"}
        mock_get_client.return_value = client
        new_id = uuid.uuid4()

        response = self.client.post(
            reverse("demo:pixbin_forms"),
            {"form_type": "upload", "title": "Second", "image": str(new_id)},
        )

        self.assertEqual(response.status_code, 302)
        client.get_status.assert_called_once_with(str(new_id))
        self.assertTrue(
            Image.objects.filter(image=new_id, uploaded_by=self.user).exists()
        )

    @patch("django_pixbin.client.get_pixbin_client")
    def test_upload_form_rejects_unknown_image(self, mock_get_client):
        client = Mock()
        client.get_status.side_effect = PixbinError("API error (404): not found")
        mock_get_client.return_value = client

        response = self.client.post(
            reverse("demo:pixbin_forms"),
            {"form_type": "upload", "title": "Ghost", "image": str(uuid.uuid4())},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "does not exist in Pixbin")
        self.assertEqual(Image.objects.count(), 1)

    def test_other_users_images_are_hidden(self):
        other = get_user_model().objects.create_user(
            email="other@example.com",
            first_name="Other",
            last_name="User",
            password="password",
        )
        self.client.force_login(other)

        response = self.client.get(
            reverse("demo:pixbin_upload"), {"image": self.image.id}
        )

        self.assertEqual(response.status_code, 404)
