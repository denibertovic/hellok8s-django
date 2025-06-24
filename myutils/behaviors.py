from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import models
from django.utils.text import slugify


class Timestampable(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Permalinkable(models.Model):
    slug = models.SlugField(max_length=255, editable=False)

    class Meta:
        abstract = True

    def get_url_kwargs(self, **kwargs):
        kwargs.update(getattr(self, "url_kwargs", {}))
        return kwargs

    def get_absolute_url(self):
        url_kwargs = self.get_url_kwargs(slug=self.slug)
        return (self.url_name, (), url_kwargs)


@receiver(pre_save)
def pre_save_slug(sender, instance, *args, **kwargs):
    if not issubclass(sender, Permalinkable):
        return
    if not instance.slug:
        source = instance._slug_source
        if len(source) > 255:
            source = instance._slug_source[0:255]
        instance.slug = slugify(instance._slug_source)
