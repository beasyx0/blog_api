from django.urls import path

from blog_api.posts.api.views import post_create, post_detail, post_update, post_delete, post_bookmarks, \
        post_bookmark, post_likes, post_dislikes, post_like, post_search, featured_posts, most_liked_posts, \
        most_disliked_posts, oldest_posts, all_posts


urlpatterns = [
    path('post/create/', post_create, name='post-create'),
    path('post/detail/', post_detail, name='post-detail'),
    path('post/update/', post_update, name='post-update'),
    path('post/delete/', post_delete, name='post-delete'),
    path('post/bookmarks/', post_bookmarks, name='post-bookmarks'),
    path('post/bookmark/', post_bookmark, name='post-bookmark'),
    path('post/likes/', post_likes, name='post-likes'),
    path('post/dislikes/', post_dislikes, name='post-dislikes'),
    path('post/like/', post_like, name='post-like'),
    path('search/', post_search, name='post-search'),
    path('featured/', featured_posts, name='posts-featured'),
    path('liked/top/', most_liked_posts, name='posts-most-liked'),
    path('disliked/top/', most_disliked_posts, name='posts-most-disliked'),
    path('oldest/', oldest_posts, name='posts-oldest'),
    path('posts/', all_posts, name='posts'),
]
