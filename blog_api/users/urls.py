from django.urls import path
from blog_api.users.api.views import user_register, user_verify_resend, user_verify, \
    user_login_refresh, user_login, user_logout, user_update, user_delete, user_password_reset_send, user_password_reset, user


urlpatterns = [
    path('user/register/', user_register, name='user-register'),
    path('user/verify/resend/', user_verify_resend, name='user-verify-resend'),
    path('user/verify/', user_verify, name='user-verify'),
    path('user/login/refresh/', user_login_refresh, name='user-login-refresh'),
    path('user/login/', user_login, name='user-login'),
    path('user/logout/', user_logout, name="user-logout"),
    path('user/update/', user_update, name='user-update'),
    path('user/delete/', user_delete, name='user-delete'),
    path('user/password/reset/send/', user_password_reset_send, name='user-password-reset-send'),
    path('user/password/reset/', user_password_reset, name='user-password-reset'),
    path('user/', user, name='user'),
]