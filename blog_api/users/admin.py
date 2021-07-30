from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from blog_api.users.models import VerificationCode, PasswordResetCode, UserFollowing
from blog_api.users.forms import UserChangeForm, UserCreationForm


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', ),
        }),
    )
    fieldsets = (
        (_("General"), {"fields": ("pub_id", "ip_address", "username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (_("Followers"), {"fields": ("following_count", "followers_count")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "last_login", 
                    "date_joined",
                )
            }
        ),
    )
    list_display = ["pub_id", "username", "email", "is_superuser", "is_active", "following_count", "followers_count",]
    search_fields = ["name", "email",]
    readonly_fields = ["pub_id", "created_at", "updated_at", "ip_address", 'followers_count', 'following_count',]
    actions = ['users_set_active_inactive',]

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        qs = qs.order_by('-created_at')
        return qs

    def users_set_active_inactive(self, request, queryset):
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save()
            else:
                user.is_active = False
                user.save()
        self.message_user(request, 'User(s) active status(\'s) changed.')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None, 
            {
                "fields": (
                    "verification_code", 
                    "user_to_verify", 
                    "code_expiration", 
                )
            }
        ),
    )
    list_display = ["verification_code", "user_to_verify", "code_expiration",]
    search_fields = []
    readonly_fields = ["verification_code","created_at", "updated_at",]


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None, 
            {
                "fields": (
                    "user", 
                    "password_reset_code", 
                    "code_expiration", 
                )
            }
        ),
    )
    list_display = ["password_reset_code", "user", "code_expiration"]
    search_fields = []
    readonly_fields = ["password_reset_code", "created_at", "updated_at",]


@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None, 
            {
                "fields": (
                    "user", 
                    "following", 
                )
            }
        ),
    )
    list_display = ["user", "following"]
    search_fields = ["user",]
