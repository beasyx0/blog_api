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

    def test_user_can_follow_unfollow_users(self):
        '''
        Ensure users can follow and unfollow other users.
        '''
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        follow_url = reverse('user-follow')

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
        self.client.force_login(user=user1)

        follow_data = {
            'follow_pub_id': user2.pub_id
        }

        follow = self.client.post(follow_url, follow_data, format='json')
        self.assertEqual(follow.status_code, HTTP_201_CREATED)
        self.assertEqual(follow.data['followed'], True)
        self.assertEqual(follow.data['message'], user2.username + ' followed successfully.')
        unfollow = self.client.post(follow_url, follow_data, format='json')
        self.assertEqual(unfollow.status_code, HTTP_200_OK)
        self.assertEqual(unfollow.data['followed'], False)
        self.assertEqual(unfollow.data['message'], user2.username + ' unfollowed successfully.')


    def test_user_cannot_follow_wronge_pub_id_to_follow(self):
        '''
        Ensure users can not follow another user with an invalid pub_id.
        '''
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        follow_url = reverse('user-follow')

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
        self.client.force_login(user=user1)

        follow_data = {
            'follow_pub_id': '8786643'
        }

        follow = self.client.post(follow_url, follow_data, format='json')
        self.assertEqual(follow.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(follow.data['followed'], False)
        self.assertEqual(follow.data['message'], 'No user found with provided pub id.')
