from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from blog_api.users.api.views import user_fallback

API_VERSION = 'api/v1/'

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path(f"{API_VERSION}users/", include('blog_api.users.urls')),
    path(f"{API_VERSION}posts/", include('blog_api.posts.urls')),
    path(f"{API_VERSION}", user_fallback, name='api-v1-fallback'),
    path("api/", user_fallback, name='api-fallback'),
    path('', user_fallback, name='fallback'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
