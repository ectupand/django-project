from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)


class GroupAdmin(admin.ModelAdmin):
    empty_value_display = 'Нетимени'
    list_display = ("title", "slug", "description")
    search_fields = ("slug",)


class CommentAdmin(admin.ModelAdmin):
    empty_value_display = 'Нетслов'
    list_display = ("text", )


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)