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
        self.user2_data = {
            'name': 'DabApps',
            'username': 'someuser001',
            'email': 'someemail1@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }

        self.blog_post_data = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt.',
        }

    def test_user_can_delete_post(self):
        print('Testing authenticated user can delete a post')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        delete_post_url = reverse('post-delete')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post_slug = Post.objects.create(
                            author=User.objects.get(email=self.user_data['email']),
                            title=self.blog_post_data['title'],
                            content=self.blog_post_data['content']).slug

        delete_post_data = {
            'post_to_delete': new_post_slug
        }
        delete_post_response = self.client.post(delete_post_url, delete_post_data, format='json')
        self.assertEqual(delete_post_response.status_code, HTTP_204_NO_CONTENT)
        print('Done.....')

    def test_user_can_only_delete_own_posts(self):
        print('Testing user can only delete his own posts')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        delete_post_url = reverse('post-delete')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg2_response = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg2_response.status_code, HTTP_201_CREATED)

        for vcode in VerificationCode.objects.all():
            verificaton_data = {
                'verification_code': vcode.verification_code
            }
            verification_response = self.client.post(verification_url, verificaton_data, format='json')
            self.assertEqual(verification_response.status_code, HTTP_200_OK)

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post_slug = Post.objects.create(
                            author=User.objects.get(email=self.user_data['email']),
                            title=self.blog_post_data['title'],
                            content=self.blog_post_data['content']).slug

        self.client.credentials()

        login_data = {
            'email': self.user2_data['email'],
            'password': self.user2_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        delete_post_data = {
            'post_to_delete': new_post_slug
        }
        delete_post_response = self.client.post(delete_post_url, delete_post_data, format='json')
        self.assertEqual(delete_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(delete_post_response.data['deleted'], False)
        self.assertEqual(delete_post_response.data['message'], 'You can only delete your own post.')
        print('Done.....')
