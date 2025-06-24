from django.db import models
from django.contrib.auth import get_user_model

from myutils.behaviors import Timestampable, Permalinkable

UserModel = get_user_model()


class Post(Timestampable, Permalinkable):
    class Meta:
        ordering = ["created_at"]

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, editable=False)

    @property
    def _slug_source(self):
        return self.title

    def __str__(self):
        return self.title
