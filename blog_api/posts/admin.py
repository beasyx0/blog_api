from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


from blog_api.posts.models import Tag, Post, Like, DisLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('slug', 'created_at', 'updated_at', 'title', 'author', 'featured', 'is_active', 'get_score',)
    list_filter = ('created_at', 'author', 'featured', 'is_active',)
    list_display_links = ('slug',)
    list_editable = ('title', 'author', 'featured', 'is_active',)
    list_per_page = 20
    list_select_related = True
    search_fields = ['title', 'author__username', 'content',]
    fieldsets = (
            (None, {
                'fields': (
                    'created_at', 'updated_at', 'slug', 
                    'title', 'author', 'content', 
                    'bookmarks', 'previouspost', 'nextpost', 
                    'estimated_reading_time', 'featured', 
                    'is_active', 'get_likes_count', 'get_dislikes_count',
                    'get_score', 'tags',
                ),
                'classes': ('wide', 'extrapretty'),
            }),
        )
    filter_horizontal = ['bookmarks', 'tags',]
    readonly_fields = ('created_at', 'updated_at', 'slug', 'estimated_reading_time', 'get_likes_count', 'get_dislikes_count', 'get_score',)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        qs = qs.defer('content').prefetch_related('tags').prefetch_related('bookmarks').select_related('author').select_related('nextpost').select_related('previouspost')
        return qs

    def get_likes_count(self, instance):
        return instance.get_likes_count()

    def get_dislikes_count(self, instance):
        return instance.get_dislikes_count()

    def get_score(self, instance):
        return instance.get_like_score()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['pub_id', 'name', 'get_post_count',]
    readonly_fields = ['pub_id', 'get_post_count',]
    list_filter = ['name',]
    search_fields = ['name',]

    def get_post_count(self, instance):
        return instance.get_post_count()


admin.site.register(Like)
admin.site.register(DisLike)
