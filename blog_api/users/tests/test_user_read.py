from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from django.urls import reverse

from blog_api.users.models import User, VerificationCode, UserFollowing
from blog_api.posts.models import Post, Like, DisLike


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
            'is_active': True
        }
        self.blog_post_data2 = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
            'is_active': False
        }

    def test_user_can_get_user_authenticated(self):
        '''
        Ensure an authenticated user can view his data.
        '''
        print('Testing user can get his own data')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_url = reverse('user')

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

        user_response = self.client.get(user_url, format='json')
        self.assertEqual(user_response.status_code, HTTP_200_OK)
        self.assertEqual(user_response.data['user']['username'], self.user_data['username'])
        print('Done.....')

    def test_user_can_get_user_public_details(self):
        '''
        Ensure an authenticated user can view the public data of another user.
        '''
        print('Testing user can get public data for another user')

        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_url = reverse('user')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg_response2 = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response2.status_code, HTTP_201_CREATED)

        for vcode in VerificationCode.objects.all():
            verificaton_data = {
                'verification_code': vcode.verification_code
            }
            self.client.post(verification_url, verificaton_data, format='json')

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

        user2 = User.objects.last()
        user_url_data = {
            'user_pub_id': user2.pub_id
        }

        user_response = self.client.get(user_url, user_url_data,format='json')
        self.assertEqual(user_response.status_code, HTTP_200_OK)
        self.assertEqual(user_response.data['user']['username'], user2.username)
        print('Done.....')

    def test_user_can_get_own_bookmarks(self):
        '''
        Ensure the user can get a list of his own bookmarks.
        '''
        print('Testing user can get his own bookmarks')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_bookmarks_url = reverse('user-bookmarks')

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

        user = User.objects.latest('created_at')

        posts = [Post.objects.create(title='this is a title', content='this is some contetnt') for _ in range(10)]
        for post in posts:
            post.bookmarks.add(user)
            post.save()

        response = self.client.get(user_bookmarks_url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(user.bookmarked_posts.all().count(), 10)
        print('Done.....')

    def test_user_can_get_own_followers(self):
        '''
        Ensure the user can get a list of his own followers.
        '''
        print('Testing a user can get his own followers')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        followers_url = reverse('user-followers')

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

        user = User.objects.latest('created_at')

        new_users = []
        for i in range(10):
            new_user = User.objects.create(username='user'+str(i), email='email'+str(i)+'@email.com', password='Testing32'+str(i))
            new_users.append(new_user)

        for new_user in new_users:
            UserFollowing.objects.create(user=new_user, following=user)
        
        response = self.client.get(followers_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(user.followers.all().count(), 10)
        print('Done.....')

    def test_user_can_get_own_following(self):
        '''
        Ensure the user can get a list of his own users hes following.
        '''
        print('Testing user can get users he follows')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        following_url = reverse('user-following')

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

        user = User.objects.latest('created_at')

        new_users = []
        for i in range(10):
            new_user = User.objects.create(username='user'+str(i), email='email'+str(i)+'@email.com', password='Testing32'+str(i))
            new_users.append(new_user)

        for new_user in new_users:
            UserFollowing.objects.create(user=user, following=new_user)
        
        response = self.client.get(following_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(user.following.all().count(), 10)
        print('Done.....')

    def test_user_can_get_own_posts(self):
        '''
        Ensure the user can get a list of his own posts.
        '''
        print('Testing a user can get his own posts')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_posts_url = reverse('user-posts')

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

        user = User.objects.latest('created_at')

        for i in range(10):
            post = Post.objects.create(author=user, title='This is a title', content='This is some contetnt')
        
        response = self.client.get(user_posts_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(user.posts.all().count(), 10)
        print('Done.....')

    def test_user_can_get_only_active_own_posts(self):
        '''
        Ensure the user can get a list of his own posts only if the post is active.
        '''
        print('Testing a user can get his own posts only if posts are active')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_posts_url = reverse('user-posts')

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

        user = User.objects.latest('created_at')

        for i in range(5):
            post = Post.objects.create(author=user, title='This is a title', content='This is some contetnt', is_active=True)

        for i in range(5):
            post = Post.objects.create(author=user, title='This is a title', content='This is some contetnt', is_active=False)
        
        response = self.client.get(user_posts_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(user.posts.all().count(), 10)
        print('Done.....')

    def test_user_can_get_posts_of_those_he_follows(self):
        '''
        Ensure the user can get a list of posts authored by users he follows.
        '''
        print('Testing user can get post of those he follows')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_following_posts_url = reverse('user-following-posts')

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

        user = User.objects.get(username=self.user_data['username'])
        user2 = User.objects.get(username=self.user2_data['username'])

        follow = UserFollowing.objects.create(
                    user=user,
                    following=user2
                )

        post = Post.objects.create(
                author=user2,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'] 
        )

        user_following_posts_response = self.client.get(user_following_posts_url)
        self.assertEqual(user_following_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_following_posts_response.data['results']), 1)
        print('Done.....')

    def test_user_can_get_posts_of_those_he_follows_only_active(self):
        '''
        Ensure the user can get a list of posts authored by users he follows only active posts.
        '''
        print('Testing user can get post of those he follows only active posts')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_following_posts_url = reverse('user-following-posts')

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

        user = User.objects.get(username=self.user_data['username'])
        user2 = User.objects.get(username=self.user2_data['username'])

        follow = UserFollowing.objects.create(
                    user=user,
                    following=user2
                )

        post = Post.objects.create(
                author=user2,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'], 
                is_active=True
            )

        post2 = Post.objects.create(
                author=user2,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'], 
                is_active=False
            )

        user_following_posts_response = self.client.get(user_following_posts_url)
        self.assertEqual(user_following_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_following_posts_response.data['results']), 1)
        self.assertEqual(user2.posts.all().count(), 2)
        print('Done.....')

    def test_user_can_get_posts_of_those_who_follow_him(self):
        '''
        Ensure the user can get a list of posts authored by users who follow him.
        '''
        print('Testing user can get posts of those who follow him')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_follower_posts_url = reverse('user-follower-posts')

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

        user = User.objects.get(username=self.user_data['username'])
        user2 = User.objects.get(username=self.user2_data['username'])

        follow = UserFollowing.objects.create(
                    user=user2,
                    following=user
                )

        post = Post.objects.create(
                author=user2,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'] 
        )

        user_follower_posts_response = self.client.get(user_follower_posts_url)
        self.assertEqual(user_follower_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_follower_posts_response.data['results']), 1)
        print('Done.....')

    def test_user_can_get_posts_of_those_who_follow_him_only_active(self):
        '''
        Ensure the user can get a list of posts authored by users who follow him only active posts.
        '''
        print('Testing user can get posts of those who follow him only active posts')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        user_follower_posts_url = reverse('user-follower-posts')

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

        user = User.objects.get(username=self.user_data['username'])
        user2 = User.objects.get(username=self.user2_data['username'])

        follow = UserFollowing.objects.create(
                    user=user2,
                    following=user
                )

        post = Post.objects.create(
                author=user2,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'], 
                is_active=True
        )
        post2 = Post.objects.create(
                author=user2,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'], 
                is_active=False
        )

        user_follower_posts_response = self.client.get(user_follower_posts_url)
        self.assertEqual(user_follower_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_follower_posts_response.data['results']), 1)
        self.assertEqual(user2.posts.all().count(), 2)
        print('Done.....')

    def test_user_can_get_all_liked_posts(self):
        '''
        Ensure a user can get all posts he liked.
        '''
        print('Testing user can get all posts he liked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')
        user_likes_url = reverse('user-likes')

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

        user_likes_response = self.client.get(user_likes_url)
        self.assertEqual(user_likes_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_likes_response.data['results']), 1)
        print('Done.....')

    def test_user_can_get_all_liked_posts_only_active(self):
        '''
        Ensure a user can get all posts he liked only active posts
        '''
        print('Testing user can get all posts he liked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')
        user_likes_url = reverse('user-likes')

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

        user = User.objects.latest('created_at')

        post = Post.objects.create(
                author=user,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'], 
                is_active=self.blog_post_data['is_active']
        )
        post2 = Post.objects.create(
                author=user,
                title=self.blog_post_data2['title'],
                content=self.blog_post_data2['content'], 
                is_active=self.blog_post_data2['is_active']
        )

        post.likes.users.add(user)
        post.save()

        post2.likes.users.add(user)
        post2.save()

        user_likes_response = self.client.get(user_likes_url)
        self.assertEqual(user_likes_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_likes_response.data['results']), 1)
        self.assertEqual(User.objects.get(username=self.user_data['username']).posts.all().count(), 2)
        print('Done.....')

    def test_user_can_get_all_disliked_posts(self):
        '''
        Ensure a user can get all posts he disliked.
        '''
        print('Testing user can get all posts he disliked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')
        user_dislikes_url = reverse('user-dislikes')

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
            'like': 'dislike',
            'post_slug': post.slug
        }
        liked_response = self.client.post(like_post_url, liked_data, format='json')
        self.assertEqual(liked_response.status_code, HTTP_201_CREATED)
        self.assertEqual(liked_response.data['liked'], False)

        user_likes_response = self.client.get(user_dislikes_url)
        self.assertEqual(user_likes_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_likes_response.data['results']), 1)
        print('Done.....')

    def test_user_can_get_all_disliked_posts_only_active(self):
        '''
        Ensure a user can get all posts he disliked only active posts
        '''
        print('Testing user can get all posts he disliked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        like_post_url = reverse('post-like')
        user_dislikes_url = reverse('user-dislikes')

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

        user = User.objects.latest('created_at')

        post = Post.objects.create(
                author=user,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content'], 
                is_active=self.blog_post_data['is_active']
        )
        post2 = Post.objects.create(
                author=user,
                title=self.blog_post_data2['title'],
                content=self.blog_post_data2['content'], 
                is_active=self.blog_post_data2['is_active']
        )

        post.dislikes.users.add(user)
        post.save()

        post2.dislikes.users.add(user)
        post2.save()

        user_likes_response = self.client.get(user_dislikes_url)
        self.assertEqual(user_likes_response.status_code, HTTP_200_OK)
        self.assertEqual(len(user_likes_response.data['results']), 1)
        self.assertEqual(User.objects.get(username=self.user_data['username']).posts.all().count(), 2)
        print('Done.....')
