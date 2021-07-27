from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from blog_api.posts.models import Post
from blog_api.posts.api.serializers import PostSerializer
from blog_api.posts.api.permissions import PostIsOwnerOrReadOnly
from blog_api.users.models import User


def get_paginated_queryset(request, qs, serializer_obj):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = serializer_obj(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes((AllowAny,))
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
    3) Grab the corresponding primary ids for next and previous posts.
    4) Add the ID for next and previous post to the request to avoid needing
       to expose sequential ID's on the front end.
    5) Serialize and attempt to save the serializer. Returns 200 or serializer.errors.
    ==========================================================================================================
    '''
    title = request.data.get('title', None)
    content = request.data.get('content', None)
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1
    featured = request.data.get('featured', None)

    request.data['author'] = request.user.id  # 2

    if next_post_slug:
        next_post_id = Post.objects.get(slug=next_post_slug).id
        request.data['nextpost'] = next_post_id

    if previous_post_slug:
        previous_post_id = Post.objects.get(slug=previous_post_slug).id  # 3
        request.data['previouspost'] = previous_post_id  # 4

    serializer = PostSerializer(data=request.data)  # 5
    if serializer.is_valid():  # 3
        serializer.save()  # 4
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
def post_detail(request):
    '''
    --Post detail view--
    1) Attempts to pull the post_slug from request. If no returns 400 and message.
    2) Attempts to pull up the post object with provided post_slug. If not found
       returns 400 and message.
    3) Serializes and returns the post object.
    '''
    post_slug = request.data.get('post_slug', None)
    if not post_slug:
        return Response({
                'message': 'Please post a valid post slug to get post.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)
    except Post.DoesNotExist:
        return Response({
                'message': 'No post found with provided slug.'
            }, status=HTTP_400_BAD_REQUEST
        )
    serialized_post = PostSerializer(post).data
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
    2) If title in request returns 400 and message.
    3) Attempt to extract the post slug from the request. If none returns 400 and message.
    4) Attempts to lookup the post to update by slug. If no returns 400 and message.
    5) Checks to make sure the user is the author of the post to update. If not returns 400 and message.
    6) If next post or previous post slugs included in request adds them to the request data. If the slug
       doesn't match catches exception and returns 400 and message. Checks that next and previous post is 
       not to self.
    7) Serializes the request data.
    8) Attempts to save the PostUpdateSerializer. Returns 200 and message. If errors returns 400 and message.
    ==========================================================================================================
    '''
    partial = request.data.get('partial', False)
    title = request.data.get('title', None)
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1

    if title:
        return Response({
                'updated': False,
                'message': 'You can not update the title.'  # 2
            }, status=HTTP_400_BAD_REQUEST
        )

    post_slug = request.data.get('slug', None)
    if not post_slug:
        return Response({
                'updated': False,
                'message': 'Something went wrong, please try again.'  # 3
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(slug=post_slug)
    except Post.DoesNotExist:
        return Response({
                'updated': False,
                'message': 'Something went wrong, please try again.'  # 4
            }, status=HTTP_400_BAD_REQUEST
        )

    if not post.author == request.user:
        return Response({
                'updated': False,
                'message': 'You can only update your own post.'  # 5
            }, status=HTTP_400_BAD_REQUEST)

    if next_post_slug:
        try:
            next_post_id = Post.objects.get(slug=next_post_slug).id  # 6
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
                    'message': 'Please post a valid next post slug to update post.',
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
                    'message': 'Please post a valid previous post slug to update post.',
                }, status=HTTP_400_BAD_REQUEST
            )

    serializer = PostSerializer(post, data=request.data, partial=partial)  # 7

    if serializer.is_valid():  # 8
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_bookmark(request):
    '''
    --Post Bookmark view--
    ==========================================================================================================
    :param: slug post_to_bookmark (required)
    1) Attempts to get the post_to_bookmark slug from request. If no returns 400 and message.
    2) Attempts to get the post to bookmark with the post_to_bookmark slug. If no returns 400 and message.
    2) Gets the current user and calls user.bookmark post(). Returns 201 for bookmarked, 200 for un-bookmarked
       or 400 if attempting to bookmark own post.
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
        Post.objects.get(slug=post_to_bookmark)  # 2
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
        if bookmarked['message'] == 'You can not bookmark your own post.':
            return Response({
                    'bookmarked': False,
                    'message': bookmarked['message']
                }, status=HTTP_400_BAD_REQUEST
            )
        else:
            return Response({
                    'bookmarked': False,
                    'message': bookmarked['message']
                }, status=HTTP_200_OK
            )
