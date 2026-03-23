from django.contrib import admin
from .models import Post, Tag, Like, Comment, Bookmark

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "location", "category", "created_at"]
    list_filter = ["category", "created_at"]
    filter_horizontal = ["tags"]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Bookmark)