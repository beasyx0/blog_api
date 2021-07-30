from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.template.defaultfilters import slugify

from blog_api.users.models import User, VerificationCode, UserFollowing
from blog_api.posts.models import Tag, Post, Like, DisLike


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

    def test_post_model_get_estimated_reading_time(self):
        '''
        Test that the model method _get_estimated_reading_time() functions as intended.
        '''

        print('Testing post model method _get_estimated_reading_time()')

        post = Post.objects.create(
                title='this is title longer than 8 words longer than 8 words',
                content='content'
            )

        self.assertEqual(post._get_estimated_reading_time(), 1)

        post.content = (post.content + ' ') * 600
        post.save()

        self.assertEqual(post.estimated_reading_time, 2)

        print('Done.....')

    def test_post_bookmark_model_method(self):
        '''
        Ensure we can cal post.bookmark() on a post instance.
        '''
        print('Testing we can call post.bookmark() on post instance')

        user = User.objects.create(
                username=self.user_data['username'],
                email=self.user_data['email'],
                password=self.user_data['password']
        )
        user.is_active = True
        user.save()

        user2 = User.objects.create(
                username=self.user2_data['username'],
                email=self.user2_data['email'],
                password=self.user2_data['password']
        )
        user2.is_active = True
        user2.save()

        post = Post.objects.create(
                author=user,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        bookmark_post_response = post.bookmark(pubid=user2.pub_id)
        self.assertEqual(bookmark_post_response['message'], f'Post {post.slug} bookmarked successfully.')
        print('Done.....')

    def test_post_bookmark_model_method_fails_wrong_user_id(self):
        '''
        Ensure we cant call post.bookmark() on a post instance with wrong user id.
        '''
        print('Testing we cant call post.bookmark() on post instance with wrong usr id')

        user = User.objects.create(
                username=self.user_data['username'],
                email=self.user_data['email'],
                password=self.user_data['password']
        )
        user.is_active = True
        user.save()

        user2 = User.objects.create(
                username=self.user2_data['username'],
                email=self.user2_data['email'],
                password=self.user2_data['password']
        )
        user2.is_active = True
        user2.save()

        post = Post.objects.create(
                author=user,
                title=self.blog_post_data['title'],
                content=self.blog_post_data['content']
            )

        bookmark_post_response = post.bookmark(pubid='3444')
        self.assertEqual(bookmark_post_response['message'], 'No user found with provided id.')
        print('Done.....')

    def test_post_manager_search(self):
        '''
        Ensure we can call Post.items.search() on the PostManager.
        '''
        print('Testing we can call Post.items.search() on the PostManager')

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

        search_term = 'lorem'
        search_results = Post.items.search(search_text=search_term)
        self.assertEqual(len(search_results), 1)
        print('Done.....')

    def test_like_dislike_str_model_methods(self):
        '''
        Ensure the str model method works on both Like and Dislike
        '''
        print('Testing Like and Dislike model str methods')
        post = Post.objects.create(
                title='this is title longer than 8 words longer than 8 words',
                content='content'
            ) 
        like = Like.objects.get(post=post)
        user = User.objects.create(
                username=self.user_data['username'],
                email=self.user_data['email'],
                password=self.user_data['password']
        )
        user.is_active = True
        user.save()

        like.users.add(user)
        like.save()

        self.assertEqual(like.__str__(), f'{like.users.all().count()} likes for {post.slug}')

        dislike = DisLike.objects.get(post=post)

        dislike.users.add(user)
        dislike.save()

        self.assertEqual(dislike.__str__(), f'{dislike.users.all().count()} dislikes for {post.slug}')




    def test_like_dislike_model_method_like_model(self):
        '''
        Ensure we can call Like.like() and Dislike.dislike()
        '''
        print('Testing we can call like() on a Like instance and dislike() on a Dislike instance')

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
        liked = post.likes.like(user.pub_id)
        self.assertEqual(liked['liked'], True)
        self.assertEqual(liked['message'], f'{user.username} liked {post.slug} successfully.')
        disliked = post.dislikes.dislike(user.pub_id)
        self.assertEqual(disliked['liked'], False)
        self.assertEqual(disliked['message'], f'{user.username} disliked {post.slug} successfully.')
        print('Done.....')

    def test_tag_str_method(self):
        print('Testing Tag model str method')

        tag = Tag.objects.create(name='tag1')

        self.assertEqual(tag.__str__(), 'tag1')

    def test_post_model_save_fails_next_post_author_not_self(self):
        '''
        Ensure the post model save method fails with next post author not self.
        '''
        print('Testing post model save method fails with next post author not self')

        user = User.objects.create(
                username=self.user_data['username'],
                email=self.user_data['email'],
                password=self.user_data['password']
        )
        user.is_active = True
        user.save()

        user2 = User.objects.create(
                username=self.user2_data['username'],
                email=self.user2_data['email'],
                password=self.user2_data['password']
        )
        user2.is_active = True
        user2.save()

        post = Post.objects.create(
                author=user,
                title='this is title longer than 8 words longer than 8 words',
                content='content'
            )
        post2 = Post.objects.create(
                author=user2,
                title='this is title longer than 8 words longer than 8 words',
                content='content'
            )

        post.nextpost = post2
        try:
            post.save()
        except ValidationError as e:
            error = e

        self.assertEqual(error.messages[0], 'Next post choices limited to author.')
