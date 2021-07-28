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
        print('Testing user can follow and unfollow users')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        follow_url = reverse('user-follow')

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

        user2 = User.objects.get(email=self.user2_data['email'])

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
        print('Done.....')

    def test_user_cannot_follow_wronge_pub_id_to_follow(self):
        '''
        Ensure users can not follow another user with an invalid pub_id.
        '''
        print('Testing user can not follow with wrong pub id for user to follow')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        follow_url = reverse('user-follow')

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

        user2 = User.objects.get(email=self.user2_data['email'])

        follow_data = {
            'follow_pub_id': '9887665554'
        }

        follow = self.client.post(follow_url, follow_data, format='json')
        self.assertEqual(follow.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(follow.data['followed'], False)
        self.assertEqual(follow.data['message'], 'No user found with provided pub id.')
        print('Done.....')
