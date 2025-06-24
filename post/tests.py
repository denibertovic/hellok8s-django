from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Post

User = get_user_model()


class PostDetailViewTests(TestCase):
    def setUp(self):
        """Create test user and post for use in tests."""
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.post = Post.objects.create(
            title="Test Post Title",
            content="This is test post content.",
            author=self.user,
        )

    def test_post_detail_view_with_slug(self):
        """Test post detail view with slug parameter returns 200 and correct content."""
        url = reverse(
            "post:detail", kwargs={"post_id": self.post.id, "slug": self.post.slug}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertEqual(response.context["post"], self.post)

    def test_post_detail_view_without_slug(self):
        """Test post detail view without slug parameter returns 200 and correct content."""
        url = reverse("post:detail-no-slug", kwargs={"post_id": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertEqual(response.context["post"], self.post)

    def test_both_url_patterns_return_same_content(self):
        """Test that both URL patterns (with and without slug) return the same content."""
        url_with_slug = reverse(
            "post:detail", kwargs={"post_id": self.post.id, "slug": self.post.slug}
        )
        url_without_slug = reverse(
            "post:detail-no-slug", kwargs={"post_id": self.post.id}
        )

        response_with_slug = self.client.get(url_with_slug)
        response_without_slug = self.client.get(url_without_slug)

        self.assertEqual(response_with_slug.status_code, 200)
        self.assertEqual(response_without_slug.status_code, 200)
        self.assertEqual(
            response_with_slug.context["post"], response_without_slug.context["post"]
        )
        self.assertEqual(response_with_slug.content, response_without_slug.content)

    def test_post_detail_view_404_for_nonexistent_post(self):
        """Test that post detail view returns 404 for non-existent post_id."""
        nonexistent_id = 99999

        # Test with slug URL
        url_with_slug = reverse(
            "post:detail", kwargs={"post_id": nonexistent_id, "slug": "some-slug"}
        )
        response = self.client.get(url_with_slug)
        self.assertEqual(response.status_code, 404)

        # Test without slug URL
        url_without_slug = reverse(
            "post:detail-no-slug", kwargs={"post_id": nonexistent_id}
        )
        response = self.client.get(url_without_slug)
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_slug_mismatch_still_works(self):
        """Test that post detail view works even with incorrect slug (slug is optional)."""
        url = reverse(
            "post:detail", kwargs={"post_id": self.post.id, "slug": "wrong-slug"}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertEqual(response.context["post"], self.post)

    def test_post_has_required_fields(self):
        """Test that post model has all required fields and behaviors."""
        self.assertEqual(self.post.title, "Test Post Title")
        self.assertEqual(self.post.content, "This is test post content.")
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(hasattr(self.post, "slug"))
        self.assertTrue(hasattr(self.post, "created_at"))
        self.assertTrue(hasattr(self.post, "updated_at"))
        self.assertEqual(str(self.post), self.post.title)
