from django.shortcuts import render, get_object_or_404
from .models import Post


def post_detail(request, post_id, slug=None):
    """Display a single post. Slug is optional and only used for SEO-friendly URLs."""
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post/detail.html", {"post": post})
