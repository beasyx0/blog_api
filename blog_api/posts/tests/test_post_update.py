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

    def test_authenticated_user_can_update_post(self):
        '''
        Ensure a user can update a post while authenticated
        '''
        print('Testing authenticated user can create new post')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

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

        update_post_data = {
            'partial': True,
            'slug': new_post_slug,
            'content': 'Lorem ipsum dolor sit amet, Praesent id fermentum orci.',
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_200_OK)
        self.assertEqual(update_post_response.data['updated'], True)
        self.assertEqual(update_post_response.data['message'], 'Post updated successfully.')
        self.assertEqual(update_post_response.data['post']['content'], 'Lorem ipsum dolor sit amet, Praesent id fermentum orci.')
        print('Done.....')

    def test_user_cannot_update_post_title(self):
        print('Testing user can not update a post title')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )

        update_post_data = {
            'partial': True,
            'title': 'This is a title.',
            'slug': new_post.slug,
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_200_OK)
        self.assertEqual(update_post_response.data['updated'], True)
        self.assertEqual(update_post_response.data['post']['title'], new_post.title)
        print('Done.....')

    def test_user_cannot_update_post_wrong_slug(self):
        print('Testing user can not update a post with wrong slug')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )

        update_post_data = {
            'partial': True,
            'slug': 'this is not a slug.',
            'content': 'this is some new updated content.',
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_post_wrong_next_post_slug(self):
        print('Testing user can not update a post with wrong next post slug')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )

        update_post_data = {
            'partial': True,
            'slug': new_post.slug,
            'content': 'This is some updated content.',
            'next_post': 'this is not a next post slug.'
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'No post found with provided next post slug.')
        print('Done.....')

    def test_user_cannot_update_post_wrong_previous_post_slug(self):
        print('Testing user can not update a post with wrong previous post slug')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )

        update_post_data = {
            'partial': True,
            'slug': new_post.slug,
            'content': 'This is some updated content',
            'previous_post': 'this is not a previous post slug.'
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'No post found with provided previous post slug.')
        print('Done.....')

    def test_user_cannot_update_post_previous_post_to_self(self):
        print('Testing user can not update a post with previous post to self.')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )

        update_post_data = {
            'partial': True,
            'slug': new_post.slug,
            'content': 'This is some updated content.',
            'previous_post': new_post.slug
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'Previous post cannot be to self.')
        print('Done.....')

    def test_user_cannot_update_post_next_post_to_self(self):
        print('Testing user can not update a post with next post to self.')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )

        update_post_data = {
            'partial': True,
            'slug': new_post.slug,
            'content': 'This is some updated content.',
            'next_post': new_post.slug
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'Next post cannot be to self.')
        print('Done.....')

    def test_user_cannot_update_post_not_author(self):
        print('Testing user can not update post if not the author')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        update_post_url = reverse('post-update')

        reg1_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg1_response.status_code, HTTP_201_CREATED)
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

        new_post = Post.objects.create(
                        author=User.objects.get(email=self.user2_data['email']),
                        title=self.blog_post_data['title'],
                        content=self.blog_post_data['content']
                    )
        update_post_data = {
            'partial': True,
            'slug': new_post.slug,
            'content': 'This is some updated content.',
        }
        update_post_response = self.client.put(update_post_url, update_post_data, format='json')
        self.assertEqual(update_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_post_response.data['updated'], False)
        self.assertEqual(update_post_response.data['message'], 'You can only update your own post.')
        print('Done.....')
