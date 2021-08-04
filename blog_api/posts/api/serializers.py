from rest_framework.serializers import ModelSerializer, ValidationError, PrimaryKeyRelatedField, SerializerMethodField

from django.db.models import Q, Count, F
from django.contrib.auth import get_user_model
User = get_user_model()

from blog_api.users.api.serializers import UserPublicSerializer
from blog_api.users.models import VerificationCode
from blog_api.posts.models import Tag, Post
from blog_api.posts.validators import validate_min_8_words


class AuthorUsernameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
        read_only_fields = fields


class TagNameSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name',]
        read_only_fields = fields


class NextPostPreviousPostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['slug', 'title',]
        read_only_fields = fields


class TagSerializer(ModelSerializer):
    post_count = SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['pub_id', 'name', 'post_count',]
        read_only_fields = fields

    def get_post_count(self, obj):
        return obj.get_post_count()


class PostCreateSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = [
            'slug', 'title', 'author', 'featured', 'content', 
            'previouspost', 'nextpost'
        ]
        read_only_fields = ['slug',]

    def create(self, validated_data):
        '''
        --Create override--
        1) Creates a new post with validated data. Defaults included to avoid requirements other
           than title and content.
        '''
        post = Post.objects.create(
            title=validated_data['title'],
            author=validated_data['author'],
            featured=validated_data.get('featured', False),
            content=validated_data['content'],
            nextpost=validated_data.get('nextpost', None), 
            previouspost=validated_data.get('previouspost', None),
        )
        return post


class PostUpdateSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = ['slug', 'content', 'nextpost', 'previouspost',]
        read_only_fields = ['slug',]


class PostDetailSerializer(ModelSerializer):

    author = UserPublicSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    bookmark_count = SerializerMethodField()
    likes_count = SerializerMethodField()
    dislikes_count = SerializerMethodField()
    like_score = SerializerMethodField()
    nextpost = NextPostPreviousPostSerializer(read_only=True)
    previouspost = NextPostPreviousPostSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'slug', 'title', 'author', 'content', 'featured', 'estimated_reading_time', 
            'previouspost', 'nextpost', 'created_at', 'updated_at', 'bookmark_count', 'likes_count', 
            'dislikes_count', 'like_score', 'tags',
        ]
        read_only_fields = fields

    def get_bookmark_count(self, obj):
        return obj.get_bookmark_count()

    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def get_dislikes_count(self, obj):
        return obj.get_dislikes_count()

    def get_like_score(self, obj):
        return obj.get_like_score()


class PostOverviewSerializer(ModelSerializer):
    author = AuthorUsernameSerializer(read_only=True)
    tags = TagNameSerializer(many=True, read_only=True)
    like_score = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'created_at', 'slug', 'title', 'author', 'featured', 
            'estimated_reading_time','tags', 'like_score',
        ]
        read_only_fields = fields

    def get_like_score(self, obj):
        return obj.get_like_score()
