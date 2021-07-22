from django.urls import path

from blog_api.posts.api.views import posts, post_create, post_update


urlpatterns = [
    path('all-posts/', posts, name='posts'),
    path('post/create/', post_create, name='post-create'),
    path('post/update/', post_update, name='post-update'),
]
