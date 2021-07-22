from datetime import timedelta
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken

from django.core import mail
from django.urls import reverse
from django.utils import timezone

from blog_api.users.models import User, VerificationCode
from blog_api.posts.models import Post


class PostTestsUpdate(APITestCase):

    def setUp(self):

        self.user_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }

        self.blog_post_data = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
        }

    def test_authenticated_user_can_update_post(self):
        print('Testing authenticated user can create new post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        update_post_url = reverse('post-update')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        user = User.objects.latest('created_at')
        self.client.force_login(user=user)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)

        new_post_slug = Post.objects.latest('created_at').slug

        update_post_data = {
            'slug': new_post_slug,
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_200_OK)
        self.assertEqual(update_post_response.data['updated'], True)
        self.assertEqual(update_post_response.data['message'], 'Post updated successfully.')
        self.assertEqual(update_post_response.data['post']['content'], self.blog_post_data['content'])

    def test_user_cannot_update_post_no_content(self):
        print('Testing authenticated user can create new post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        update_post_url = reverse('post-update')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        user = User.objects.latest('created_at')
        self.client.force_login(user=user)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)

        update_post_data = {
            'slug': Post.objects.latest('created_at').slug,
            'next_post_slug': Post.objects.latest('created_at').slug,

        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)

    def test_user_cannot_update_post_title(self):
        print('Testing user can not update a post title')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        update_post_url = reverse('post-update')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        user = User.objects.latest('created_at')
        self.client.force_login(user=user)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)

        update_post_data = {
            'title': 'This is a title.',
            'slug': Post.objects.latest('created_at').slug,
            'next_post_slug': Post.objects.latest('created_at').slug,

        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)

    def test_user_cannot_update_post_wrong_slug(self):
        print('Testing user can not update a post with wrong slug')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        update_post_url = reverse('post-update')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        user = User.objects.latest('created_at')
        self.client.force_login(user=user)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)

        update_post_data = {
            'slug': 'this is not a slug.',
            'content': self.blog_post_data['content'],
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)

    def test_user_cannot_update_post_wrong_next_post_slug(self):
        print('Testing user can not update a post with wrong next post slug')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        update_post_url = reverse('post-update')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        user = User.objects.latest('created_at')
        self.client.force_login(user=user)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)

        update_post_data = {
            'slug': Post.objects.latest('created_at').slug,
            'content': self.blog_post_data['content'],
            'next_post': 'this is not a next post slug.'
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'Please post a valid next post slug to update post.')

    def test_user_cannot_update_post_wrong_previous_post_slug(self):
        print('Testing user can not update a post with wrong previous post slug')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        update_post_url = reverse('post-update')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        user = User.objects.latest('created_at')
        self.client.force_login(user=user)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)

        update_post_data = {
            'slug': Post.objects.latest('created_at').slug,
            'content': self.blog_post_data['content'],
            'previous_post': 'this is not a previous post slug.'
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'Please post a valid previous post slug to update post.')