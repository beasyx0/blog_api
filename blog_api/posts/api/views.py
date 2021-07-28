from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import AnonRateThrottle

from blog_api.posts.models import Post
from blog_api.posts.api.serializers import AuthorBookmarkSerializer, PostSerializer, PostUpdateSerializer
from blog_api.posts.api.permissions import PostIsOwnerOrReadOnly
from blog_api.users.models import User


def get_paginated_queryset(request, qs, serializer_obj):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = serializer_obj(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes((AllowAny,))
@throttle_classes([AnonRateThrottle])
def posts(request):
    '''
    --All posts view--
    ==========================================================================================================
    Returns nested representations of all posts. Paginates the quereyset.
    ==========================================================================================================
    '''
    posts_to_paginate = \
        Post.objects.prefetch_related('bookmarks').select_related('previouspost').select_related('nextpost')         \
                                                                                            .filter(is_active=True)
    all_posts = get_paginated_queryset(request, posts_to_paginate, PostSerializer)

    return all_posts


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
    4) Serialize and attempt to save the serializer. Returns 200 or serializer.errors.
    ==========================================================================================================
    '''
    title = request.data.get('title', None)
    content = request.data.get('content', None)
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1
    featured = request.data.get('featured', None)

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

    serializer = PostSerializer(data=request.data)  # 4
    if serializer.is_valid():
        serializer.save()
        return Response({
                'created': True,
                'posts': serializer.data
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
    ==========================================================================================================
    '''
    partial = request.data.get('partial', False)
    title = request.data.get('title', None)
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1


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
            }, status=HTTP_400_BAD_REQUEST)

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

    serializer = PostUpdateSerializer(post, data=request.data, partial=partial)  # 6

    if serializer.is_valid():  # 7
        serializer.save()
        return Response({
                'updated': True,
                'message': 'Post updated successfully.',
                'post': serializer.data
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
    all_post_bookmarks = get_paginated_queryset(request, bookmarks, AuthorBookmarkSerializer)
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
    --Post like view--
    ==========================================================================================================
    :param: str slug (required)
    1) Checks for slug in request. If no returns 400 and message.
    2) Attempts to get the post with the provided slug. If no returns 400 and message.
    3) Gets the current user from request.user.
    4) Calls like_post() on the user instance. Returns 201 for liked, returns 200 for disliked else 400 and 
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

    try:
        post = Post.objects.get(slug=post_slug)  # 2
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        return Response({
                'liked': False,
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )

    user = request.user  # 3

    liked = user.like_post(post.slug)  # 4
    
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
                }, status=HTTP_200_OK
            )
        else:
            return Response({
                    'liked': liked['liked'],
                    'message': liked['message']
                }, status=HTTP_400_BAD_REQUEST
            )
