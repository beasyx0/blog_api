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
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'name': 'DrSuess',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_200_OK)
        self.assertEqual(update_response.data['updated'], True)
        print('Done.....')

    def test_user_can_update_username_only(self):
        '''
        Ensure a user can update his username only.
        '''
        print('Testing user can update name')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'username': 'DrSuess',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_200_OK)
        self.assertEqual(update_response.data['updated'], True)
        print('Done.....')

    def test_user_can_update_name_only(self):
        '''
        Ensure a user can update his name only.
        '''
        print('Testing user can update name')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'name': 'DrSuess',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_200_OK)
        self.assertEqual(update_response.data['updated'], True)
        print('Done.....')

    def test_user_can_update_username_only(self):
        '''
        Ensure a user can update his name only.
        '''
        print('Testing user can update name')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'username': 'DrSuess',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
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
            'name': 'DrSuess',
            'partial': True
        }
        response = self.client.put(update_url, data, format='json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        print('Done.....')

    def test_user_cannot_update_without_including_something_in_request(self):
        print('Testing user cannot update without including something in the request')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {}
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        self.assertEqual(update_response.data['message'], 'You need to include at least one field to update.')
        print('Done.....')

    def test_user_cannot_update_blank_username(self):
        '''
        Ensure a user cannot update with a blank username.
        '''
        print('Testing user cannot update with blank username')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'username': '',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_email(self):
        '''
        Ensure the user cannot update the email address.
        '''
        print('Testing cannot update email')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        update_url = reverse('user-update')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(verification_response.data['message'], 'Code verified and the user is now active! You may now log in.')

        user = User.objects.all()[0]
        self.client.force_login(user=user)

        update_data = {
            'email': 'someotheremail@email.com',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        self.assertEqual(update_response.data['message'], 'You cannot update your email.')
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
            'username': self.user_data['username'],
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_username_more_than_3_special_chars(self):
        '''
        Ensure user cannot update username with more than 3 special characters.
        '''
        print('Testing user cannot update username with more than 3 special characters')
        register_url = reverse('user-register')
        self.client.post(register_url, self.user_data, format='json')
        VerificationCode.objects.all()[0].verify()
        user = User.objects.get(username=self.user_data['username'])
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'username': 'franky@@@@',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_name_with_special_chars(self):
        '''
        Ensure user cannot update name with special characters.
        '''
        print('Testing user cannot update username with more than 3 special characters')
        register_url = reverse('user-register')
        self.client.post(register_url, self.user_data, format='json')
        VerificationCode.objects.all()[0].verify()
        user = User.objects.get(username=self.user_data['username'])
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'name': 'franky@@@@',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')

    def test_user_cannot_update_username_with_spaces(self):
        '''
        Ensure user cannot update username with spaces.
        '''
        print('Testing user cannot update username with any spaces')
        register_url = reverse('user-register')
        self.client.post(register_url, self.user_data, format='json')
        VerificationCode.objects.all()[0].verify()
        user = User.objects.get(username=self.user_data['username'])
        self.client.force_login(user=user)
        update_url = reverse('user-update')
        update_data = {
            'username': 'frad nky@@',
            'partial': True
        }
        update_response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.data['updated'], False)
        print('Done.....')
