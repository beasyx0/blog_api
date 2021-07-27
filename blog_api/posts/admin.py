from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


from blog_api.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('slug', 'created_at', 'updated_at', 'title', 'author', 'estimated_reading_time', 'featured', 'is_active',)
    list_filter = ('created_at', 'author', 'featured', 'is_active',)
    list_display_links = ('slug',)
    list_editable = ('title', 'author', 'featured', 'is_active',)
    list_per_page = 50
    list_select_related = True
    search_fields = ['title', 'author', 'content',]
    fieldsets = (
            (None, {
                'fields': (
                    'created_at', 'updated_at', 'slug', 
                    'title', 'author', 'content', 
                    'bookmarks', 'previouspost', 'nextpost', 
                    'estimated_reading_time', 
                    'featured', 'is_active',
                ),
                'classes': ('wide', 'extrapretty'),
            }),
        )
    filter_horizontal = ['bookmarks',]
    readonly_fields = ('created_at', 'updated_at', 'slug', 'estimated_reading_time',)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        qs = qs.defer('content').prefetch_related('bookmarks').select_related('author').select_related('nextpost').select_related('previouspost')
        return qs
