from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


from blog_api.posts.models import Post

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     fieldsets = (
#         (_("General"), {"fields": ("user", "many",)}),
#     )
#     list_display = ["user",]
#     # search_fields = ["name", "email",]
#     # readonly_fields = ["pub_id", "created_at", "updated_at", "ip_address",]

admin.site.register(Post)