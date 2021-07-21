from django.urls import path

from blog_api.posts.api.views import posts, post_create


urlpatterns = [
    path('all-posts/', posts, name='posts'),
    path('post/create/', post_create, name='post-create'),
]
