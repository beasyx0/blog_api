from datetime import timedelta
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from django.urls import reverse

from blog_api.users.models import User, VerificationCode
from blog_api.posts.models import Post


class PostTestsRead(APITestCase):

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
            'email': 'someemai1l@email.com',
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

    def test_user_can_get_all_posts(self):
        '''
        Ensure a user can get all posts.
        '''
        print('Testing a user can get a list of all posts')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        all_posts_url = reverse('posts')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)

        user = User.objects.latest('created_at')
        for i in range(10):
            Post.objects.create(**self.blog_post_data)

        all_posts_response = self.client.get(all_posts_url)
        self.assertEqual(all_posts_response.status_code, 200)
        self.assertEqual(Post.objects.all().count(), 10)
        print('Done.....')

    def test_user_can_get_all_featured_posts(self):
        '''
        Ensure a user can get all posts that are featured.
        '''
        print('Testing user can get all posts that are featured')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        featured_posts_url = reverse('posts-featured')

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

        self.blog_post_data['featured'] = True
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        self.blog_post_data['featured'] = False
        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        featured_posts_response = self.client.get(featured_posts_url)
        self.assertEqual(featured_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(featured_posts_response.data['results']), 1)

        print('Done.....')

    def test_user_can_get_all_featured_posts_only_active(self):
        '''
        Ensure a user can get all posts that are featured only active posts
        '''
        print('Testing user can get all posts that are featured only active')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        featured_posts_url = reverse('posts-featured')

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

        self.blog_post_data['featured'] = True
        create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response.data['created'], True)

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        inactive_post = Post.objects.first()
        inactive_post.is_active = False
        inactive_post.save()

        featured_posts_response = self.client.get(featured_posts_url)
        self.assertEqual(featured_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(featured_posts_response.data['results']), 1)

        print('Done.....')

    def test_user_can_get_all_most_liked_posts(self):
        '''
        Ensure a user can get all posts that are most liked in order by most liked.
        '''
        print('Testing user can get all posts that are most liked ordered by most liked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        most_liked_posts_url = reverse('posts-most-liked')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg_response2 = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response2.status_code, HTTP_201_CREATED)

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        user1 = User.objects.first()
        user2 = User.objects.last()

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        post1.likes.users.add(user1)
        post1.likes.users.add(user2)

        post2.likes.users.add(user2)

        most_liked_posts_response = self.client.get(most_liked_posts_url)
        self.assertEqual(most_liked_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(most_liked_posts_response.data['results'][0]['slug'], post1.slug)

        print('Done.....')

    def test_user_can_get_all_most_liked_posts_only_active(self):
        '''
        Ensure a user can get all posts that are most liked in order by most liked only active posts.
        '''
        print('Testing user can get all posts that are most liked ordered by most liked only active')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        most_liked_posts_url = reverse('posts-most-liked')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg_response2 = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response2.status_code, HTTP_201_CREATED)

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        user1 = User.objects.first()
        user2 = User.objects.last()

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        post1.likes.users.add(user1)
        post1.likes.users.add(user2)

        post2.likes.users.add(user2)

        post1.is_active = False
        post1.save()

        most_liked_posts_response = self.client.get(most_liked_posts_url)
        self.assertEqual(most_liked_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(most_liked_posts_response.data['results']), 1)

        print('Done.....')

    def test_user_can_get_all_most_disliked_posts(self):
        '''
        Ensure a user can get all posts that are most disliked in order by most disliked.
        '''
        print('Testing user can get all posts that are most disliked ordered by most disliked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        most_disliked_posts_url = reverse('posts-most-disliked')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg_response2 = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response2.status_code, HTTP_201_CREATED)

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        user1 = User.objects.first()
        user2 = User.objects.last()

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        post1.dislikes.users.add(user1)
        post1.dislikes.users.add(user2)

        post2.dislikes.users.add(user2)

        most_disliked_posts_response = self.client.get(most_disliked_posts_url)
        self.assertEqual(most_disliked_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(most_disliked_posts_response.data['results'][0]['slug'], post1.slug)

        print('Done.....')

    def test_user_can_get_all_most_disliked_posts_only_active(self):
        '''
        Ensure a user can get all posts that are most disliked in order by most disliked only active posts.
        '''
        print('Testing user can get all posts that are most disliked ordered by most disliked only active')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        most_disliked_posts_url = reverse('posts-most-disliked')

        reg_response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
        reg_response2 = self.client.post(register_url, self.user2_data, format='json')
        self.assertEqual(reg_response2.status_code, HTTP_201_CREATED)

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        user1 = User.objects.first()
        user2 = User.objects.last()

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        post1.dislikes.users.add(user1)
        post1.dislikes.users.add(user2)

        post2.dislikes.users.add(user2)

        post1.is_active = False
        post1.save()

        most_disliked_posts_response = self.client.get(most_disliked_posts_url)
        self.assertEqual(most_disliked_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(most_disliked_posts_response.data['results']), 1)

        print('Done.....')

    def test_user_can_get_oldest_posts(self):
        '''
        Ensure a user can get all posts in order by oldest.
        '''
        print('Testing user can get all posts by oldest')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        oldest_posts_url = reverse('posts-oldest')

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        post1.created_at = post1.created_at - timedelta(days=7)
        post1.save()

        oldest_posts_response = self.client.get(oldest_posts_url)
        self.assertEqual(oldest_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(oldest_posts_response.data['results'][0]['slug'], post1.slug)

    def test_user_can_get_oldest_posts_only_active(self):
        '''
        Ensure a user can get all posts in order by oldest only active posts
        '''
        print('Testing user can get all posts by oldest only active posts')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        oldest_posts_url = reverse('posts-oldest')

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        post1.is_active = False
        post1.save()

        oldest_posts_response = self.client.get(oldest_posts_url)
        self.assertEqual(oldest_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(len(oldest_posts_response.data['results']), 1)

    def test_user_can_get_most_bookmarked_posts(self):
        '''
        Ensure a user can get all posts in order by most bookmarked.
        '''
        print('Testing user can get all posts by most bookmarked')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        most_bookmarked_posts_url = reverse('posts-most-bookmarked')

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        user = User.objects.first()

        post1.bookmarks.add(user)
        post1.save()

        most_bookmarked_posts_response = self.client.get(most_bookmarked_posts_url)
        self.assertEqual(most_bookmarked_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(most_bookmarked_posts_response.data['results'][0]['slug'], post1.slug)

    def test_user_can_get_most_bookmarked_posts_only_active(self):
        '''
        Ensure a user can get all posts in order by most bookmarked only active
        '''
        print('Testing user can get all posts by most bookmarked only active')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        most_bookmarked_posts_url = reverse('posts-most-bookmarked')

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

        create_post_response2 = self.client.post(create_post_url, self.blog_post_data, format='json')
        self.assertEqual(create_post_response2.status_code, HTTP_201_CREATED)
        self.assertEqual(create_post_response2.data['created'], True)

        post1 = Post.objects.first()
        post2 = Post.objects.last()

        user = User.objects.first()

        post1.bookmarks.add(user)
        post1.save()

        post2.is_active = False
        post2.save()

        most_bookmarked_posts_response = self.client.get(most_bookmarked_posts_url)
        self.assertEqual(most_bookmarked_posts_response.status_code, HTTP_200_OK)
        self.assertEqual(most_bookmarked_posts_response.data['results'][0]['slug'], post1.slug)
        self.assertEqual(len(most_bookmarked_posts_response.data['results']), 1)

    def test_user_can_get_all_tag_choices(self):
        '''
        Ensure a user can get all tags choices for frontend create post.
        '''
        print('Testing a user can get a list of all tags for frontend create post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        all_tags_url = reverse('tags')

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

        all_tags_response = self.client.get(all_tags_url)
        self.assertEqual(all_tags_response.status_code, HTTP_200_OK)
        self.assertEqual(len(all_tags_response.data['results']), 3)

    def test_user_can_get_all_next_post_previous_post_choices(self):
        '''
        Ensure a user can get all next/previous post choices for frontend create post.
        '''
        print('Testing a user can get a list of all next/previous post choices for frontend create post')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        create_post_url = reverse('post-create')
        next_previous_choices_url = reverse('post-next-previous')

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
        
        for i in range(5):
            create_post_response = self.client.post(create_post_url, self.blog_post_data, format='json')
            self.assertEqual(create_post_response.status_code, HTTP_201_CREATED)
            self.assertEqual(create_post_response.data['created'], True)

        next_previous_choices_response = self.client.get(next_previous_choices_url)
        self.assertEqual(next_previous_choices_response.status_code, HTTP_200_OK)
        self.assertEqual(len(next_previous_choices_response.data['results']), 5)
