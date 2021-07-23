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
        self.blog_post_data = {
            'title': 'A really cool title for some really cool blog post by a really cool developer.',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed facilisis nunc id orci hendrerit, id tempor lorem tincidunt. Praesent id fermentum orci. Proin malesuada est sed nisl aliquam, ac congue nibh sagittis. Vestibulum sed ipsum vulputate, sodales neque auctor, mollis odio. Nullam sit amet mattis ante. Aenean mi sapien, aliquet eget sapien ac, finibus accumsan erat. Donec pretium risus faucibus ultrices egestas. In at aliquam magna. Pellentesque vitae felis est. Sed at augue ipsum. Cras mi nunc, efficitur a malesuada ac, vulputate a mauris. Mauris congue congue dui, eu maximus ante vulputate nec. Vivamus in lorem nec quam ultricies tincidunt ultrices in lectus. Quisque semper posuere libero sit amet tempor. In quis augue quam. Mauris eget risus in ante congue mattis a in est. Duis porta ornare placerat. In lacinia felis metus, ac dignissim est ultrices eu. Aenean nec massa eget mi maximus tempor. In quis leo condimentum, vulputate urna eget, accumsan ex. Vestibulum bibendum ante ac lobortis convallis.',
        }

    # READ
    def test_user_can_get_user_authenticated(self):
        '''
        Ensure an authenticated user can view his data.
        '''
        register_url = reverse('user-register')
        user_url = reverse('user')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        response = self.client.get(user_url)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_user_can_get_own_bookmarks(self):
        '''
        Ensure the user can get a list of his own bookmarks.
        '''
        register_url = reverse('user-register')
        user_url = reverse('user')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)

        posts = [Post.objects.create(title='this is a title', content='this is some contetnt') for _ in range(10)]
        for post in posts:
            post.bookmarks.add(user)
            post.save()

        response = self.client.get(user_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.bookmarked_posts.all().count(), 10)

    def test_user_can_get_own_followers(self):
        '''
        Ensure the user can get a list of his own followers.
        '''
        register_url = reverse('user-register')
        user_url = reverse('user')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)

        new_users = []
        for i in range(10):
            new_user = User.objects.create(username='user'+str(i), email='email'+str(i)+'@email.com', password='Testing32'+str(i))
            new_users.append(new_user)

        for new_user in new_users:
            UserFollowing.objects.create(user=new_user, following=user)
        
        response = self.client.get(user_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.followers.all().count(), 10)

    def test_user_can_get_own_following(self):
        '''
        Ensure the user can get a list of his own users following.
        '''
        register_url = reverse('user-register')
        user_url = reverse('user')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)

        new_users = []
        for i in range(10):
            new_user = User.objects.create(username='user'+str(i), email='email'+str(i)+'@email.com', password='Testing32'+str(i))
            new_users.append(new_user)

        for new_user in new_users:
            UserFollowing.objects.create(user=user, following=new_user)
        
        response = self.client.get(user_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.following.all().count(), 10)

    def test_user_can_get_own_posts(self):
        '''
        Ensure the user can get a list of his own posts.
        '''
        register_url = reverse('user-register')
        user_url = reverse('user')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)

        new_posts = []
        for i in range(10):
            post = Post.objects.create(author=user, title='This is a title', content='This is some contetnt')
            new_posts.append(post)
        
        response = self.client.get(user_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.posts.all().count(), 10)

    def test_user_cannot_get_user_unauthenticated(self):
        '''
        Ensure an unauthenticated user cannot view his data.
        '''
        response = self.client.get(reverse("user"))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
