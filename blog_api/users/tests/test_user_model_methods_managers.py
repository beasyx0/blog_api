from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from django.urls import reverse

from blog_api.users.models import User, VerificationCode, UserFollowing
from blog_api.posts.models import Post


class UserTestsRead(APITestCase):

    def setUp(self):
        self.user_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user2_data = {
            'name': 'DabApps',
            'username': 'someuser001',
            'email': 'someemail1@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.blog_post_data = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
        }

    def test_user_like_post_model_method(self):
        '''
        Ensure we can call user.like_post() on a user instance.
        '''
        print('Testing we can call user.like_post() on a user instance')

        user = User.objects.create(
                username=self.user_data['username'],
                email=self.user_data['email'],
                password=self.user_data['password']
        )
        user.is_active = True
        user.save()

        post = Post.objects.create(
                author=user,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        liked = user.like_post(post.slug)
        self.assertEqual(liked['liked'], True)
        self.assertEqual(liked['message'], f'{user.username} liked {post.slug} successfully.')
        disliked = user.like_post(post.slug)
        self.assertEqual(disliked['liked'], False)
        self.assertEqual(disliked['message'], f'{user.username} disliked {post.slug} successfully.')

        print('Done.....')
