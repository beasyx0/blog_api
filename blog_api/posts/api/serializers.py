from rest_framework.serializers import ModelSerializer, ValidationError

from django.contrib.auth import get_user_model
User = get_user_model()

from blog_api.users.api.serializers import UserSerializer
from blog_api.users.models import VerificationCode
from blog_api.posts.models import Post



class AuthorBookmarkSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['pub_id', 'username',]


class NextPostPreviousPostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['slug', 'title',]

    def to_representation(self, instance):
        post_slug = instance.slug
        return post_slug


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        # depth = 5
        fields = [
            'slug', 'title', 'author', 'featured',
            'estimated_reading_time', 'content', 
            'bookmarks', 'previouspost', 'nextpost',
        ]

    def to_representation(self, instance):
        '''
        Nested serializers.
        '''
        self.fields['author'] = AuthorBookmarkSerializer()
        self.fields['bookmarks'] = AuthorBookmarkSerializer(many=True)
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
