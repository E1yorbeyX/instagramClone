from django.contrib import admin
from posts.models import Post, PostCommet, PostLike, CommetLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'created_at']
    search_fields = ['id', 'author__username', 'caption']


@admin.register(PostCommet)
class PostCommetAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'created_at']
    search_fields = ['id', 'post', 'commet']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created_at']
    search_fields = ['id', 'post', 'author']


@admin.register(CommetLike)
class CommetLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'commet', 'created_at']
    search_fields = ['id', 'author', 'commet']