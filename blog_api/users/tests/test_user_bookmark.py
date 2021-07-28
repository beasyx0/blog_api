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

    def test_user_can_bookmark_posts(self):
        '''
        Ensure users can bookmark  posts.
        '''
        print('Testing user can bookmark posts')
        create_post_url = reverse('post-create')
        bookmark_url = reverse('post-bookmark')

        user1 = User.objects.create(
            username=self.user_data['username'], 
            email=self.user_data['email'], 
            password=self.user_data['password'],
            is_active=True
        )
        user2 = User.objects.create(
            username=self.user2_data['username'], 
            email=self.user2_data['email'], 
            password=self.user2_data['password'],
            is_active=True
        )

        post = Post.objects.create(
                author=user1,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        self.client.force_login(user=user2)

        bookmark_data = {
            'post_to_bookmark': post.slug,
        }

        bookmark_response = self.client.post(bookmark_url, bookmark_data, format='json')
        self.assertEqual(bookmark_response.status_code, HTTP_201_CREATED)
        self.assertEqual(bookmark_response.data['bookmarked'], True)
        self.assertEqual(bookmark_response.data['message'], 'Post ' + post.slug + ' bookmarked successfully.')

    def test_user_can_unbookmark_posts(self):
        '''
        Ensure a user can un bookmark a post
        '''
        print('Testing user can bookmark and un-bookmark posts')
        create_post_url = reverse('post-create')
        bookmark_url = reverse('post-bookmark')

        user1 = User.objects.create(
            username=self.user_data['username'], 
            email=self.user_data['email'], 
            password=self.user_data['password'],
            is_active=True
        )
        user2 = User.objects.create(
            username=self.user2_data['username'], 
            email=self.user2_data['email'], 
            password=self.user2_data['password'],
            is_active=True
        )

        post = Post.objects.create(
                author=user1,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        post.bookmarks.add(user2)
        post.save()

        self.client.force_login(user=user2)

        bookmark_data = {
            'post_to_bookmark': post.slug,
        }

        bookmark_response = self.client.post(bookmark_url, bookmark_data, format='json')
        self.assertEqual(bookmark_response.status_code, HTTP_200_OK)
        self.assertEqual(bookmark_response.data['bookmarked'], False)
        self.assertEqual(bookmark_response.data['message'], 'Post ' + post.slug + ' un-bookmarked successfully.')

    def test_user_cannot_bookmark_own_post(self):
        '''
        Ensure a user can not bookmark own post.
        '''
        print('Testing user can not bookmark own posts')
        create_post_url = reverse('post-create')
        bookmark_url = reverse('post-bookmark')

        user = User.objects.create(
            username=self.user_data['username'], 
            email=self.user_data['email'], 
            password=self.user_data['password'],
            is_active=True
        )

        post = Post.objects.create(
                author=user,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        self.client.force_login(user=user)

        bookmark_data = {
            'post_to_bookmark': post.slug,
        }

        bookmark_response = self.client.post(bookmark_url, bookmark_data, format='json')
        self.assertEqual(bookmark_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(bookmark_response.data['bookmarked'], False)
        self.assertEqual(bookmark_response.data['message'], 'You can not bookmark your own post.')

    def test_user_cannot_bookmark_wrong_slug(self):
        '''
        Ensure a user can not bookmark post wrong slug.
        '''
        print('Testing user can not bookmark posts wrong slug')
        create_post_url = reverse('post-create')
        bookmark_url = reverse('post-bookmark')

        user1 = User.objects.create(
            username=self.user_data['username'], 
            email=self.user_data['email'], 
            password=self.user_data['password'],
            is_active=True
        )
        user2 = User.objects.create(
            username=self.user2_data['username'], 
            email=self.user2_data['email'], 
            password=self.user2_data['password'],
            is_active=True
        )

        post = Post.objects.create(
                author=user1,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        post.bookmarks.add(user2)
        post.save()

        self.client.force_login(user=user2)

        bookmark_data = {
            'post_to_bookmark': '878768',
        }

        bookmark_response = self.client.post(bookmark_url, bookmark_data, format='json')
        self.assertEqual(bookmark_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(bookmark_response.data['bookmarked'], False)
        self.assertEqual(bookmark_response.data['message'], 'No post found with provided slug.')

    def test_user_cannot_bookmark_inactive_post(self):
        print('Testing user can not bookmark inactive post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        post_create_url = reverse('post-create')
        bookmark_url = reverse('post-bookmark')

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

        new_post_data = {
            'author': User.objects.first(),
            'title': self.blog_post_data['title'],
            'content': self.blog_post_data['content']
        }
        new_post_response = self.client.post(post_create_url, self.blog_post_data, format='json')
        self.assertEqual(new_post_response.status_code, HTTP_201_CREATED)

        post = Post.objects.latest('created_at')
        post.is_active = False
        post.save()

        bookmark_data = {
            'post_to_bookmark': post.slug
        }
        bookmark_response = self.client.post(bookmark_url, bookmark_data, format='json')
        self.assertEqual(bookmark_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(bookmark_response.data['message'], 'No post found with provided slug.')

