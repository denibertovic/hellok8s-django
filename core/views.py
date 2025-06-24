from django.shortcuts import render
from post.models import Post


def index(request):
    posts = Post.objects.all().order_by("-created_at")
    context = {"posts": posts}
    return render(request, "core/index.html", context)
