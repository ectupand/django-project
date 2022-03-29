from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)

admin.site.register(Post, PostAdmin)
