from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response

from blog_api.posts.models import Post
from blog_api.posts.api.serializers import PostSerializer
from blog_api.posts.api.permissions import PostIsOwnerOrReadOnly
from blog_api.users.models import User


@api_view(['GET'])
@permission_classes((AllowAny,))
def posts(request):
    '''
    '''
    posts = Post.objects.prefetch_related('bookmarks').select_related('previouspost').select_related('nextpost')
    
    serialized_posts = PostSerializer(posts, many=True).data
    return Response({
        'posts': serialized_posts
    }, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, PostIsOwnerOrReadOnly,))
def post_create(request):
    '''
    --Post create view--
    1) Extract the required inputs from the request. If not any returns 400 and message.
    2) Set the current user as the author in request.
    3) Grab the corresponding primary ids for next and previous posts.
    4) Add the ID for next and previous post to the request to avoid needing
       to expose sequential ID's on the front end.
    5) Serialize and attempt to save the serializer. Returns 200 or serializer.errors.
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
    if serializer.is_valid():
        serializer.save()
        serialized_post = serializer.data
        return Response({
            'posts': serialized_post
        }, status=HTTP_201_CREATED)
    return Response({
            'posts': serializer.errors
        }, status=HTTP_400_BAD_REQUEST)
