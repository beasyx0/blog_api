from django.urls import path

from blog_api.posts.api.views import posts, post_create, post_detail, post_update, post_delete, post_bookmarks, post_bookmark, post_search, post_like


urlpatterns = [
    path('all-posts/search/', post_search, name='post-search'),
    path('all-posts/', posts, name='posts'),
    path('post/create/', post_create, name='post-create'),
    path('post/detail/', post_detail, name='post-detail'),
    path('post/update/', post_update, name='post-update'),
    path('post/delete/', post_delete, name='post-delete'),
    path('post/bookmarks/', post_bookmarks, name='post-bookmarks'),
    path('post/bookmark/', post_bookmark, name='post-bookmark'),
    path('post/like/', post_like, name='post-like'),
]
