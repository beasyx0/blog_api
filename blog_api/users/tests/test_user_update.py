from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from blog_api.users.models import User, VerificationCode


class UserTestsUpdate(APITestCase):

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
            'username': 'someuser000',
            'email': 'someemail000@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }

    # UPDATE
    def test_user_can_update_authenticated(self):
        '''
        Ensure a user can update authenticated with the correct format.
        '''
        print('Testing user can update while authenticated')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.last()
        vcode = VerificationCode.objects.last()
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'name': 'Dr Suess',
            'partial': True
        }
        update_response = self.client.post(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_200_OK)
        self.assertEqual(update_response.data['updated'], True)
        print('Done.....')

    def test_user_cannot_update_unauthenticated(self):
        '''
        Ensure a user cannot update his data unauthenticated.
        '''
        print('Testing user cannot update while unauthenticated')
        update_url = reverse('user-update')
        data = {
            'name': 'Dr Suess',
            'partial': True
        }
        response = self.client.post(update_url, data, format='json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        print('Done.....')

    def test_user_cannot_update_blank_username(self):
        '''
        Ensure a user cannot update with a blank username.
        '''
        print('Testing user cannot update with blank username')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.last()
        vcode = VerificationCode.objects.last()
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'username': '',
            'partial': True
        }
        update_response = self.client.post(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_blank_email(self):
        '''
        Ensure a user cannot update his data with no email.
        '''
        print('Testing user cannot update with blank email')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.last()
        vcode = VerificationCode.objects.last()
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'email': '',
            'partial': True
        }
        update_response = self.client.post(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_wrong_email_format(self):
        '''
        Ensure a user cannot udate with the wrong email format.
        '''
        print('Testing user cannot update with wrong email format')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.last()
        vcode = VerificationCode.objects.last()
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'email': 'bhjgvgy',
            'partial': True
        }
        update_response = self.client.post(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_unique_username(self):
        '''
        Ensure user cannot update with a username already taken.
        '''
        print('Testing user cannot update unique username')
        register_url = reverse('user-register')
        self.client.post(register_url, self.user_data, format='json')
        self.client.post(register_url, self.user2_data, format='json')
        vcodes = VerificationCode.objects.all()
        for code in vcodes:
            code.verify()
        user = User.objects.get(username=self.user2_data['username'])
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'email': 'someuser00',
            'partial': True
        }
        update_response = self.client.post(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')
