from rest_framework.serializers import ModelSerializer, ValidationError, PrimaryKeyRelatedField, SerializerMethodField, CharField

from django.contrib.auth import get_user_model
User = get_user_model()

from blog_api.users.models import VerificationCode
from blog_api.posts.models import Post
from blog_api.posts.validators import validate_title_min_8_words


class AuthorBookmarkSerializer(ModelSerializer):

    follow_counts = SerializerMethodField()
    post_count = SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['pub_id', 'username', 'follow_counts', 'post_count',]

    def get_follow_counts(self, obj):
        return obj.get_following_follower_count()

    def get_post_count(self, obj):
        return obj.get_post_count()


class NextPostPreviousPostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['slug', 'title',]

    def to_representation(self, instance):
        post_slug = instance.slug
        return post_slug


class PostSerializer(ModelSerializer):

    author = PrimaryKeyRelatedField(allow_null=True, queryset=User.objects.all(), required=False)

    title = CharField(
        max_length=255,
        validators=[validate_title_min_8_words,]
        )

    nextpost = \
        PrimaryKeyRelatedField(
            allow_null=True, required=False, 
            queryset=Post.objects.prefetch_related('bookmarks')
                                    .select_related('previouspost').select_related('nextpost').filter(is_active=True), 
    )
    previouspost = \
        PrimaryKeyRelatedField(
            allow_null=True, required=False, 
            queryset=Post.objects.prefetch_related('bookmarks')
                                    .select_related('previouspost').select_related('nextpost').filter(is_active=True), 
    )

    class Meta:
        model = Post
        fields = [
            'slug', 'title', 'author', 'featured',
            'estimated_reading_time', 'content', 
            'previouspost', 'nextpost', 'created_at', 
            'updated_at',
        ]

    def to_representation(self, instance):
        '''
        Nested serializers.
        '''
        self.fields['author'] = AuthorBookmarkSerializer()
        self.fields['nextpost'] = NextPostPreviousPostSerializer()
        self.fields['previouspost'] = NextPostPreviousPostSerializer() 
        return super(PostSerializer, self).to_representation(instance)

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

    title = SerializerMethodField()
    estimated_reading_time = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'slug', 'title', 'author', 'featured',
            'estimated_reading_time', 'content', 
            'previouspost', 'nextpost', 'created_at', 
            'updated_at',
        ]
        read_only_fields = [
            'slug', 'title', 'author', 'estimated_reading_time', 
        ]

    def get_title(self, obj):
        return obj.title

    def get_author(self, obj):
        return obj.author.username

    def get_estimated_reading_time(self, obj):
        return obj.estimated_reading_time

    def to_representation(self, instance):
        '''
        Nested serializers.
        '''
        self.fields['author'] = AuthorBookmarkSerializer()
        self.fields['nextpost'] = NextPostPreviousPostSerializer()
        self.fields['previouspost'] = NextPostPreviousPostSerializer() 
        return super(PostUpdateSerializer, self).to_representation(instance)
