from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
    readonly_fields = (
        "author",
        "slug",
    )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super(PostAdmin, self).save_model(request, obj, form, change)


admin.site.register(Post, PostAdmin)
