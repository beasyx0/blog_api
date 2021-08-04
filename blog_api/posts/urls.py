from django.urls import path

from blog_api.posts.api.views import post_create, post_detail, post_update, post_delete, post_bookmarks, \
        post_bookmark, post_likes, post_dislikes, post_like, all_tags, all_tags_by_post_count, all_tag_posts, next_previous_posts, post_search, \
        featured_posts, most_liked_posts, most_disliked_posts, oldest_posts, most_bookmarked_posts, all_posts, posts_fallback


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
    path('tags/', all_tags, name='tags'),
    path('tags/by-post-count/', all_tags_by_post_count, name='tags-by-post-count'),
    path('tags/tag/posts/', all_tag_posts, name='tag-posts'),
    path('next-previous-posts/', next_previous_posts, name='post-next-previous'),
    path('search/', post_search, name='post-search'),
    path('featured/', featured_posts, name='posts-featured'),
    path('most-liked/', most_liked_posts, name='posts-most-liked'),
    path('most-disliked/', most_disliked_posts, name='posts-most-disliked'),
    path('oldest/', oldest_posts, name='posts-oldest'),
    path('most-bookmarked/', most_bookmarked_posts, name='posts-most-bookmarked'),
    path('posts/', all_posts, name='posts'),
    path('', posts_fallback, name='posts-fallback'),
]
