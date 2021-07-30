from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import AnonRateThrottle

from django.db.models import Q, Count, F

from blog_api.posts.models import Tag, Post
from blog_api.posts.api.serializers import AuthorBookmarkLikedSerializer, NextPostPreviousPostSerializer, TagSerializer, PostSerializer, PostUpdateSerializer
from blog_api.users.models import User
from blog_api.posts.models import update_post_counts


def get_paginated_queryset(request, qs, serializer_obj, page_size=10):
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    page = paginator.paginate_queryset(qs, request)
    serializer = serializer_obj(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def all_posts(request):
    '''
    --All posts view--
    ==========================================================================================================
    Returns nested representations of all posts. Paginates the quereyset.
    ==========================================================================================================
    '''
    posts_to_paginate = \
        Post.objects.prefetch_related('bookmarks')\
                    .select_related('previouspost').select_related('nextpost')\
                    .filter(is_active=True)

    all_posts = get_paginated_queryset(request, posts_to_paginate, PostSerializer)

    return all_posts


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def featured_posts(request):
    '''
    --All featured posts view--
    ==========================================================================================================
    Returns nested representations of all posts that are featured. Paginates the queryset.
    ==========================================================================================================
    '''
    featured_posts_to_paginate = Post.items.featured()

    featured_posts = get_paginated_queryset(request, featured_posts_to_paginate, PostSerializer)

    return featured_posts


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def most_liked_posts(request):
    '''
    --All most liked posts view--
    ==========================================================================================================
    Returns nested representations of all posts by most liked. Paginates the queryset.
    ==========================================================================================================
    '''
    most_liked_posts_to_paginate = Post.items.most_liked()

    most_liked_posts = get_paginated_queryset(request, most_liked_posts_to_paginate, PostSerializer)

    return most_liked_posts


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def most_disliked_posts(request):
    '''
    --All most disliked posts view--
    ==========================================================================================================
    Returns nested representations of all posts by most disliked. Paginates the queryset.
    ==========================================================================================================
    '''
    most_disliked_posts_to_paginate = Post.items.most_disliked()

    most_disliked_posts = get_paginated_queryset(request, most_disliked_posts_to_paginate, PostSerializer)

    return most_disliked_posts


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def oldest_posts(request):
    '''
    --All oldest posts view--
    ==========================================================================================================
    Returns nested representations of all posts by oldest. Paginates the quereyset.
    ==========================================================================================================
    '''
    posts_to_paginate = Post.items.oldest_posts()

    oldest_posts = get_paginated_queryset(request, posts_to_paginate, PostSerializer)

    return oldest_posts


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def most_bookmarked_posts(request):
    '''
    --Most bookmarked posts view--
    ==========================================================================================================
    Returns nested representations of all posts by most bookmarked. Paginates the quereyset.
    ==========================================================================================================
    '''
    posts_to_paginate = Post.items.most_bookmarked()

    most_bookmarked_posts = get_paginated_queryset(request, posts_to_paginate, PostSerializer)

    return most_bookmarked_posts


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def next_previous_posts(request):
    '''
    :param: str updating (required)
    :param: str post_slug
    --All next/previous post choices--
    1) Extract the updating and post_slug keywords from request. If updating is True we leave the post 
       out of the queryset (no next/previous posts to self)
    '''
    updating = request.data.get('updating', None)
    post_slug = request.data.get('post_slug', None)

    if updating is not None and not post_slug:
        return Response({
                    'message': 'Please post a valid post slug if updating else exclude the updating keyword.'
                }, status=HTTP_400_BAD_REQUEST
            )
    if updating and post_slug:
        try:
            post = Post.objects.get(slug=post_slug)
            if not post.is_active:
                raise Post.DoesNotExist()
            next_previous_posts_to_paginate = Post.objects.filter(author=request.user, is_active=True).exclude(slug=post_slug)  # if action is update we exclude the post being updated
        except Post.DoesNotExist:
            return Response({
                    'message': 'No post found with provided slug.'
                }, status=HTTP_400_BAD_REQUEST
            )
    else:
        next_previous_posts_to_paginate = Post.objects.filter(author=request.user, is_active=True)

    all_next_previous_posts = get_paginated_queryset(request, next_previous_posts_to_paginate, NextPostPreviousPostSerializer, page_size=1000)

    return all_next_previous_posts


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_create(request):
    '''
    --Post create view--
    ==========================================================================================================
    :param: str title (required)
    :param: str content (required)
    :param: str next_post_slug.
    :param: str previous_post_slug
    :param: boolean featured.
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    :returns: boolean created.
    1) Extract the required inputs from the request. If not set to None.
    2) Set the current user as the author in request.
    3) Grab the corresponding primary ids for next and previous posts and adds them to the request.
        If not found or if post is inactive returns 400 and message.
    4) Serialize and attempt to save the serializer. If error returns serializer.errors.
    5) If any post tags were included in the request, adds them to the new post.
    6) Updates any objects with a post count attribute.
    7) Returns serialized post.
    ==========================================================================================================
    '''
    title = request.data.get('title', None)
    content = request.data.get('content', None)
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1
    featured = request.data.get('featured', None)
    post_tags = request.data.get('post_tags', None)

    request.data['author'] = request.user.id  # 2

    if next_post_slug:
        try:
            next_post = Post.objects.get(slug=next_post_slug)  # 3
            if not next_post.is_active:
                raise Post.DoesNotExist()
            request.data['nextpost'] = next_post.id
        except Post.DoesNotExist:
            return Response({
                    'created': False,
                    'message': 'No post found with provided next post slug.'
                }, status=HTTP_400_BAD_REQUEST
            )

    if previous_post_slug:
        try:
            previous_post = Post.objects.get(slug=previous_post_slug)
            if not previous_post.is_active:
                raise Post.DoesNotExist()
            request.data['previouspost'] = previous_post.id
        except Post.DoesNotExist:
            return Response({
                    'created': False,
                    'message': 'No post found with provided previous post slug.'
                }, status=HTTP_400_BAD_REQUEST
            )

    if post_tags:
        tag_set = Tag.items.comma_to_qs(post_tags)
    
    serializer = PostSerializer(data=request.data)  # 4
    if serializer.is_valid():
        serializer.save()

        new_post = Post.objects.get(slug=serializer.data['slug'])

        if post_tags:
            new_post.tags.clear()
            new_post.tags.add(*tag_set)  # 5
            new_post.save()
            
        update_post_counts([new_post.author])  # 6
        new_post = PostSerializer(new_post)  # serializer was already saved, have to reserialize to get tags if any
        return Response({
                'created': True,
                'post': new_post.data  # 7
            }, status=HTTP_201_CREATED
        )
    else:
        return Response({
            'created': False,
            'message': serializer.errors
        }, status=HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def post_detail(request):
    '''
    --Post detail view--
    ==========================================================================================================
    :param: str post_slug (required)
    1) Attempts to pull the post_slug from request. If no returns 400 and message.
    2) Attempts to pull up the post object with provided post_slug. If not found
       returns 400 and message.
    3) Serializes and returns the post object.
    ==========================================================================================================
    '''
    post_slug = request.data.get('post_slug', None)  # 1
    if not post_slug:
        return Response({
                'message': 'Please post a valid post slug to get post.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)  # 2
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )
    serialized_post = PostSerializer(post).data  # 3
    return Response({
            'post': serialized_post
        }, status=HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def post_update(request):
    '''
    ---Post update view---
    ==========================================================================================================
    :param: str content (required)
    :param: boolean partial
    :param: str next_post_slug.
    :param: str previous_post_slug
    :param: str post_slug (required)
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    :returns: boolean updated.
    1) Extract variables from the request, set defaults to avoid errors.
    2) Attempt to extract the post slug from the request. If none returns 400 and message.
    3) Attempts to lookup the post to update by slug. If no returns 400 and message.
    4) Checks to make sure the user is the author of the post to update. If not returns 400 and message.
    5) If next post or previous post slugs included in request adds the post ID to the request data. If the slug
       doesn't match catches exception and returns 400 and message. Checks that next and previous post is 
       not to self.
    6) Serializes the request data.
    7) Attempts to save the PostUpdateSerializer. Returns 200 and message. If errors returns 400 and message.
    8) If any post tags were included in the request, adds them to the post.
    9) Updates any objects with a post count attribute.
    10) Returns serialized post.
    ==========================================================================================================
    '''
    partial = request.data.get('partial', False)
    title = request.data.get('title', None)
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1
    post_tags = request.data.get('post_tags', None)


    post_slug = request.data.get('slug', None)
    if not post_slug:
        return Response({
                'updated': False,
                'message': 'Please post a valid post slug to update post.'  # 2
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'updated': False,
                'message': 'No post found with provided slug.'  # 3
            }, status=HTTP_400_BAD_REQUEST
        )

    if not post.author == request.user:
        return Response({
                'updated': False,
                'message': 'You can only update your own post.'  # 4
            }, status=HTTP_400_BAD_REQUEST
        )

    if next_post_slug:
        try:
            next_post_id = Post.objects.get(slug=next_post_slug).id  # 5
            if next_post_id == post.id:
                return Response({
                        'updated': False,
                        'message': 'Next post cannot be to self.'
                    }, status=HTTP_400_BAD_REQUEST
                )
            request.data['nextpost'] = next_post_id
        except Post.DoesNotExist:
            return Response({
                    'updated': False,
                    'message': 'No post found with provided next post slug.',
                }, status=HTTP_400_BAD_REQUEST
            )

    if previous_post_slug:
        try:
            previous_post_id = Post.objects.get(slug=previous_post_slug).id
            if previous_post_id == post.id:
                return Response({
                        'updated': False,
                        'message': 'Previous post cannot be to self.'
                    }, status=HTTP_400_BAD_REQUEST
                )
            request.data['previouspost'] = previous_post_id
        except Post.DoesNotExist:
            return Response({
                    'updated': False,
                    'message': 'No post found with provided previous post slug.',
                }, status=HTTP_400_BAD_REQUEST
            )

    if post_tags:
        tag_set = Tag.items.comma_to_qs(post_tags)

    serializer = PostUpdateSerializer(post, data=request.data, partial=partial)  # 6

    if serializer.is_valid():  # 7
        serializer.save()

        updated_post = Post.objects.get(slug=serializer.data['slug'])

        if post_tags:
            updated_post.tags.clear()
            updated_post.tags.add(*tag_set)  # 8
            updated_post.save()
            
        update_post_counts([updated_post.author])  # 9
        updated_post = PostSerializer(updated_post)  # serializer was already saved, have to reserialize to get tags if any
        return Response({
                'updated': True,
                'message': 'Post updated successfully.',
                'post': updated_post.data  # 10
            }, status=HTTP_200_OK
        )
    else:
        return Response({
                'updated': False,
                'message': serializer.errors
            }, status=HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def post_bookmarks(request):
    '''
    --All post bookmarks view--
    ==========================================================================================================
    :param: post_slug str (required)
    Returns all bookmark users for post instance.
    ==========================================================================================================
    '''
    post_slug = request.data.get('post_slug', None)
    if not post_slug:
        return Response({
                'message': 'Please post a valid post slug to get bookmark users.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    bookmarks = post.bookmarks.all()
    all_post_bookmarks = get_paginated_queryset(request, bookmarks, AuthorBookmarkSerializer, page_size=30)
    return all_post_bookmarks


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_bookmark(request):
    '''
    --Post Bookmark view--
    ==========================================================================================================
    :param: slug post_to_bookmark (required)
    1) Attempts to get the post_to_bookmark slug from request. If no returns 400 and message.
    2) Attempts to get the post to bookmark with the post_to_bookmark slug. If no returns 400 and message.
    2) Gets the current user and calls user.bookmark post(). Returns 201 for bookmarked. Returns 200 for 
       unbookmarked else 400 and message.
    ==========================================================================================================
    '''
    post_to_bookmark = request.data.get('post_to_bookmark', None)  # 1
    if not post_to_bookmark:
        return Response({
                'bookmarked': False,
                'message': 'Please post a valid post slug to bookmark.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_to_bookmark)  # 2
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'bookmarked': False,
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    user = request.user
    bookmarked = user.bookmark_post(post_to_bookmark)  # 3

    if bookmarked['bookmarked']:
        return Response({
            'bookmarked': True,
            'message': bookmarked['message']
        }, status=HTTP_201_CREATED
    )
    else:
        if bookmarked['message'] == f'Post {post.slug} un-bookmarked successfully.':
            return Response({
                    'bookmarked': False,
                    'message': bookmarked['message']
                }, status=HTTP_200_OK
            )
        else:
            return Response({
                    'bookmarked': False,
                    'message': bookmarked['message']
                }, status=HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_delete(request):
    '''
    --Post delete view--
    ==========================================================================================================
    :param: str post_to_delete (required)
    1) Attempts to get the post_to_delete from the request. If no returns 400 and message.
    2) Attempts to pull up the post with the provided slug. If no returns 400 and message.
    3) Sets the post as inactive (deleted). Returns 200 and message.
    ==========================================================================================================
    '''
    post_to_delete = request.data.get('post_to_delete')
    if not post_to_delete:
        return Response({
                'deleted': False,
                'message': 'Please post a valid post slug to delete.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_to_delete)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'deleted': False,
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    if not post.author == request.user:
        return Response({
                'deleted': False,
                'message': 'You can only delete your own post.'
            }, status=HTTP_400_BAD_REQUEST
        )

    post.is_active = False
    post.save()

    update_post_counts([post.author])

    return Response({
            'deleted': True,
            'message': 'Post deleted successfully.'
        }, status=HTTP_204_NO_CONTENT
    )


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def post_search(request):
    '''
    --Post search view--
    ==========================================================================================================
    :param: str searh_term (required)
    1) Attempts to get search_term from request. If no returns 400 and message.
    2) Checks that the provided search term is greater than 3 charactars. If no returns 400 and message.
    3) Calls search() on the PostManager. Returns all matching posts. Paginates queryset.
    ==========================================================================================================
    '''
    search_term = request.data.get('search_term', None)  # 1
    if not search_term:
        return Response({
                'message': 'Please post a valid search term to search posts.'
            }, status=HTTP_400_BAD_REQUEST
        )

    if not len(search_term) >= 3:
        return Response({
                'message': 'Search term must be 3 characters long.'  # 2
            }, status=HTTP_400_BAD_REQUEST
        )

    search_results = Post.items.search(search_text=search_term)  # 3
    if not search_results:
        return Response({
                'message': 'No posts found with provided search term.'
            }, status=HTTP_400_BAD_REQUEST
        )

    all_posts = get_paginated_queryset(request, search_results, PostSerializer)

    return all_posts


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_like(request):
    '''
    --Post like/dislike view--
    ==========================================================================================================
    :param: str slug (required)
    :param: str like (required) e.g 'like' or 'dislike'
    1) Checks for slug in request. If no returns 400 and message.
    2) Checks for like keyword in request. If none returns 400 and messsage.
    3) Checks that the like keyword is either `like` or `dislike`. If no returns 400 and message.
    4) Attempts to get the post with the provided slug. If no returns 400 and message.
    5) Gets the current user from request.user.
    6) Calls like_post() on the user instance. Returns 201 for liked, returns 200 for disliked else 400 and 
       message.
    ==========================================================================================================
    '''
    post_slug = request.data.get('post_slug', None)  # 1
    if not post_slug:
        return Response({
                'liked': False,
                'message': 'Please post a valid post slug to like post.'
            }, status=HTTP_400_BAD_REQUEST
        )

    like = request.data.get('like', None)  # 2
    if not like:
        return Response({
                'liked': False,
                'message': 'Please post a valid like or dislike keyword to like or dislike post.'
            }, status=HTTP_400_BAD_REQUEST
        )

    liked_choices = ['like', 'dislike',]  # 3
    if not like in liked_choices:
        return Response({
                'liked': False,
                'message': 'Please post either `like` or `dislike` keyword to like or dislike post.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)  # 4
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'liked': False,
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    user = request.user  # 5

    liked = user.like_post(post.slug, like)  # 6
    
    if liked['liked']:
        return Response({
                'liked': liked['liked'],
                'message': liked['message']
            }, status=HTTP_201_CREATED
        )
    else:
        if liked['message'] == user.username + ' disliked ' + post.slug + ' successfully.':
            return Response({
                    'liked': liked['liked'],
                    'message': liked['message']
                }, status=HTTP_201_CREATED
            )
        else:
            return Response({
                    'liked': liked['liked'],
                    'message': liked['message']
                }, status=HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def all_tags(request):
    '''
    --All tags view--
    ==========================================================================================================
    Return all tag names and pub_id's.
    ==========================================================================================================
    '''
    tags = Tag.objects.all()
    all_tags = get_paginated_queryset(request, tags, TagSerializer, page_size=1000)
    
    return all_tags


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def post_likes(request):
    '''
    --All post likes view--
    ==========================================================================================================
    Return all the users who liked a post. Paginates the queryset.
    :param: str post_slug (required)
    1) Checks for post slug in request. If no returns 400 and message.
    2) Attempts to get the post with provided post slug. If no or post is inactive returns 400 and message.
    3) Gets all the users who liked the post. Paginates queryset. Returns 200 and message.
    ==========================================================================================================
    '''
    post_slug = request.data.get('post_slug', None)
    if not post_slug:
        return Response({
                'message': 'Please post a valid post slug to get likes.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    users_liked = post.likes.users.all()
    all_users_liked = get_paginated_queryset(request, users_liked, AuthorBookmarkLikedSerializer, page_size=30)
    return all_users_liked


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def post_dislikes(request):
    '''
    --All post dislikes view--
    ==========================================================================================================
    Return all the users who disliked a post. Paginates the queryset.
    :param: str post_slug (required)
    1) Checks for post slug in request. If no returns 400 and message.
    2) Attempts to get the post with provided post slug. If no or post is inactive returns 400 and message.
    3) Gets all the users who liked the post. Paginates queryset. Returns 200 and message.
    ==========================================================================================================
    '''
    post_slug = request.data.get('post_slug', None)
    if not post_slug:
        return Response({
                'message': 'Please post a valid post slug to get likes.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    users_disliked = post.dislikes.users.all()
    all_users_disliked = get_paginated_queryset(request, users_disliked, AuthorBookmarkLikedSerializer, page_size=30)
    return all_users_disliked


@api_view(['GET', 'POST', 'PUT', 'PATCH'])
@permission_classes((AllowAny,))
def posts_fallback(request):
    '''
    Fallback to display a nice message.
    '''
    return Response({
            'message': 'Please no.'
        }, status=HTTP_403_FORBIDDEN
    )
