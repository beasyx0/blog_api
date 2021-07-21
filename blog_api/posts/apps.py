from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = 'blog_api.posts'

    def ready(self):
        try:
            import blog_api.posts.signals  # noqa F401
        except ImportError:
            pass
