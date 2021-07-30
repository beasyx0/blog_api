from datetime import timedelta
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken

from django.core import mail
from django.urls import reverse
from django.utils import timezone

from blog_api.users.models import User, VerificationCode
from blog_api.posts.models import Tag, Post


class PostTestsCreate(APITestCase):

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

        self.blog_post_data_with_tags_str = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
            'post_tags': 'tag1, tag2, tag3'
        }

        self.blog_post_data_no_title = {
            'title': '',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
        }

        self.blog_post_data_no_content = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': '',
        }

    def test_authenticated_user_can_create_new_post(self):
        '''
        Ensure a user can create a new post authenticated.
        '''
        print('Testing authenticated user can create new post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(Post.objects.all()[0].title, 'A really cool title for some really cool blog post by a really cool developer.')
        print('Done.....')

    def test_authenticated_user_can_create_new_post_with_tags(self):
        '''
        Ensure a user can create a new post with tags
        '''
        print('Testing authenticated user can create new post with tags')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data_with_tags_str, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        new_post = Post.objects.first()

        self.assertEqual(len(new_post.tags.all()), 3)
        self.assertEqual(new_post.tags.all()[0].name, 'tag1')

        print('Done.....')

    def test_user_cannot_create_post_unauthenticated(self):
        '''
        Ensure a user can not create post unauthenticated
        '''
        print('Testing user cannot create a new post unauthenticated.')
        create_post_url = reverse('post-create')
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.all().count(), 0)
        print('Done.....')

    def test_user_cannot_create_post_no_content(self):
        '''
        Ensure a user cannot create a post with no content.
        '''
        print('Testing user can not create post no content')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg2_response = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data_no_content, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(create_post_response.data['created'], False)
        print('Done.....')

    def test_user_cannot_create_post_no_title(self):
        '''
        Ensure a user cannot create a post with no title.
        '''
        print('Testing user can not create post with not title')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg2_response = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data_no_title, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(create_post_response.data['created'], False)
        print('Done.....')

    def test_user_cannot_create_post_title_not_8_words(self):
        '''
        Ensure a user cannot create a post with the title being less than 8 words.
        '''
        print('Testing user can not create post with title less than 8 words')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        self.blog_post_data['title'] = 'This is four words'
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(create_post_response.data['created'], False)
        print('Done.....')

    def test_user_cannot_create_post_wrong_next_post_slug(self):
        '''
        Ensure a user cannot create a post with wrong next post slug.
        '''
        print('Testing user can not create post with the wrong next post slug')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        self.blog_post_data['next_post'] = 'kllkjlkjkljlkjlkjlkj'
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(create_post_response.data['created'], False)
        self.assertEqual(create_post_response.data['message'], 'No post found with provided next post slug.')
        print('Done.....')

    def test_user_cannot_create_post_wrong_previous_post_slug(self):
        '''
        Ensure a user cannot create a post with wrong previous post slug.
        '''
        print('Testing user can not create post with the wrong previous post slug')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        self.blog_post_data['previous_post'] = 'kllkjlkjkljlkjlkjlkj'
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(create_post_response.data['created'], False)
        self.assertEqual(create_post_response.data['message'], 'No post found with provided previous post slug.')
        print('Done.....')

    def test_user_can_like_post(self):
        '''
        Ensure a user can like a post.
        '''
        print('Testing user can like a post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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

        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        post = Post.objects.first()

        liked_data = {
            'like': 'like',
            'post_slug': post.slug
        }
        liked_response = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response.status_code, HTTP_201_CREATED)
        self.assertEqual(liked_response.data['liked'], True)
        self.assertEqual(liked_response.data['message'], self.user_data['username'] + ' liked ' + post.slug + ' successfully.')
        post.refresh_from_db()
        self.assertEqual(post.likes_count, 1)

        print('Done.....')

    def test_post_like_count_after_like_dislike(self):
        '''
        Ensure the post like and dislike counts are correct after user likes and dislikes post.
        '''
        print('Testing the post like and dislike counts are correct after user likes and dislikes post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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

        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        post = Post.objects.first()

        liked_data = {
            'like': 'like',
            'post_slug': post.slug
        }
        liked_response = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response.status_code, HTTP_201_CREATED)
        self.assertEqual(liked_response.data['liked'], True)
        post.refresh_from_db()
        self.assertEqual(post.likes_count, 1)
        self.assertEqual(post.dislikes_count, 0)
        self.assertEqual(post.score, 1)

        liked_data['like'] = 'dislike'
        liked_response2 = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(liked_response2.data['liked'], False)
        post.refresh_from_db()
        self.assertEqual(post.likes_count, 0)
        self.assertEqual(post.dislikes_count, 1)
        self.assertEqual(post.score, -1)

        print('Done.....')

    def test_user_cannot_like_post_wrong_slug(self):
        print('Testing user can not like a post with wrong slug')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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

        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        post = Post.objects.first()

        liked_data = {
            'like': 'like',
            'post_slug': '7654323'
        }
        liked_response = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(liked_response.data['liked'], False)
        self.assertEqual(liked_response.data['message'], 'No post found with provided slug.')
        print('Done.....')

    def test_user_cannot_like_post_wrong_like_keyword(self):
        print('Testing user can not like a post without including the `like` or `dislike` keyword')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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

        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        post = Post.objects.first()

        liked_data = {
            'like': 'li',
            'post_slug': post.slug
        }
        liked_response = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(liked_response.data['liked'], False)
        self.assertEqual(liked_response.data['message'], 'Please post either `like` or `dislike` keyword to like or dislike post.')
        print('Done.....')

    def test_user_cannot_like_post_no_like_keyword(self):
        print('Testing user can not like a post without including the like keyword')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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

        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        post = Post.objects.first()

        liked_data = {
            'post_slug': post.slug
        }
        liked_response = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(liked_response.data['liked'], False)
        self.assertEqual(liked_response.data['message'], 'Please post a valid like or dislike keyword to like or dislike post.')
        print('Done.....')

    def test_user_cannot_create_new_post_next_post_not_his_post(self):
        '''
        Ensure a user can not create a new post with next post to a post he didnt author.
        '''
        print('Testing user can not create new post with next post he didnt author')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg2_response = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        post1 = Post.objects.latest('created_at')

        self.client.credentials()
        login2_data = {
            'email': self.user2_data['email'],
            'password': self.user2_data['password']
        }
        new_login2 = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login2.data['access'])

        self.blog_post_data['nextpost'] = post1.slug
        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_400_BAD_REQUEST)

    def test_user_cannot_create_new_post_previous_post_not_his_post(self):
        '''
        Ensure a user can not create a new post with previous post to a post he didnt author.
        '''
        print('Testing user can not create new post with previous post he didnt author')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg2_response = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        post1 = Post.objects.latest('created_at')

        self.client.credentials()

        login2_data = {
            'email': self.user2_data['email'],
            'password': self.user2_data['password']
        }
        new_login2 = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login2.data['access'])

        self.blog_post_data['previouspost'] = post1.slug
        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_400_BAD_REQUEST)

    def test_user_post_count_updates_creating_new_post(self):
        '''
        Ensure a user's post count gets incremented upon creating a new post
        '''
        print('Testing user post count increments upon creating new post.')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

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

        user = User.objects.first()
        self.assertEqual(user.post_count, 0)
        
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        user.refresh_from_db()
        self.assertEqual(user.post_count, 1)
        print('Done.....')
