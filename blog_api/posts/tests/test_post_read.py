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

    def test_user_can_get_all_posts_unauthenticated(self):
        '''
        Ensure a user can get all posts unauthenticated.
        '''
        print('Testing a user can get a list of all posts unauthenticated')
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

# TODO: Write tests for get requests with params.

    # def test_user_can_get_all_post_bookmark_users(self):
    #     '''
    #     Ensure a user can get all the users who bookmarked a post instance
    #     '''
    #     print('Testing user can get all bookmark users for post instance')
    #     register_url = reverse('user-register')
    #     verification_url = reverse('user-verify')
    #     login_url = reverse('user-login')
    #     post_bookmarks_url = reverse('post-bookmarks')

    #     reg_response = self.client.post(register_url, self.user_data, format='json')
    #     self.assertEqual(reg_response.status_code, HTTP_201_CREATED)
    #     reg2_response = self.client.post(register_url, self.user2_data, format='json')
    #     self.assertEqual(reg_response.status_code, HTTP_201_CREATED)

    #     for vcode in VerificationCode.objects.all():
    #         verificaton_data = {
    #             'verification_code': vcode.verification_code
    #         }
    #         verification_response = self.client.post(verification_url, verificaton_data, format='json')
    #         self.assertEqual(verification_response.status_code, HTTP_200_OK)

    #     post = Post.objects.create(
    #             author=User.objects.get(username=self.user_data['username']),
    #             title=self.blog_post_data['title'],
    #             content=self.blog_post_data['content']
    #     )
    #     post.bookmarks.set([User.objects.get(username=self.user2_data['username'])])
    #     post.save()

    #     login_data = {
    #         'email': self.user_data['email'],
    #         'password': self.user_data['password']
    #     }
    #     new_login = self.client.post(login_url, login_data, format='json')
    #     self.assertEqual(new_login.status_code, HTTP_200_OK)

    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_login.data['access'])

    #     post_bookmarks_data = {
    #         'post_to_bookmark': post.slug
    #     }

    #     post_bookmarks_response = self.client.get(post_bookmarks_url, data=post_bookmarks_data, format='json')
    #     self.assertEqual(post_bookmarks_response.status_code, HTTP_200_OK)

    #     print('Done.....')
