from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response

from blog_api.posts.models import Post
from blog_api.posts.api.serializers import PostSerializer, UpdatePostSerializer 
from blog_api.posts.api.permissions import PostIsOwnerOrReadOnly
from blog_api.users.models import User


@api_view(['GET'])
@permission_classes((AllowAny,))
def posts(request):
    '''
    --All posts view--
    ==========================================================================================================
    Returns nested representations of all posts.
    ==========================================================================================================
    '''
    posts = Post.objects.prefetch_related('bookmarks')      \
                        .select_related('previouspost')     \
                        .select_related('nextpost')
    
    serialized_posts = PostSerializer(posts, many=True).data
    return Response({
        'posts': serialized_posts
    }, status=HTTP_200_OK)


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
    3) Checks that there's at least one argument in the request. If no returns 400 and message.
    4) Attempts to lookup the post to update by slug. If no returns 400 and message.
    5) If next post or previous post slugs included in request adds them to the request data. If the slug
       doesn't match catches exception and returns 400 and message.
    6) Serializes the request data.
    7) Attempts to save the PostUpdateSerializer. Returns 200 and message. If errors returns 400 and message.
    ==========================================================================================================
    '''
    partial = request.data.get('partial', False)  # ?? Is partial even working ??
    next_post_slug = request.data.get('next_post', None)
    previous_post_slug = request.data.get('previous_post', None)  # 1

    post_slug = request.data.get('slug', None)
    if not post_slug:
        return Response({
                'updated': False,
                'message': 'Something went wrong, please try again.'  # 2
            }, status=HTTP_400_BAD_REQUEST
        )

    if not request.data.keys():
        return Response({
                'updated': False,
                'message': 'You need to include at least one field to update.'  # 3
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

    if next_post_slug:
        try:
            next_post_id = Post.objects.get(slug=next_post_slug).id  # 5
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
            request.data['previouspost'] = previous_post_id
        except Post.DoesNotExist:
            return Response({
                    'updated': False,
                    'message': 'Please post a valid previous post slug to update post.',
                }, status=HTTP_400_BAD_REQUEST
            )

    serializer = UpdatePostSerializer(post, data=request.data, partial=partial)  # 6

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
