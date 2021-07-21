from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone

from blog_api.users.models import User, VerificationCode


class UserTestsDelete(APITestCase):

    def setUp(self):
        self.user_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }

    # DELETE
    def test_user_can_delete_mark_inactive_blacklist_token(self):
        '''
        Ensure when a user deletes account that its marked inactive and the token is blacklisted.
        '''
        print('Testing user can delete (mark user inactive) and blacklists token')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')  # register, verify and login user
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)


        obtain_pair_url = reverse('user-login')  # grab the tokens for the delete endpoint
        obtain_pair_data = {
            'username': self.user_data['username'],
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        obtain_pair_response = self.client.post(obtain_pair_url, obtain_pair_data, format='json')
        access = obtain_pair_response.data['access']
        refresh = obtain_pair_response.data['refresh']

        delete_url = reverse('user-delete')  # send the required params to the endpoint
        delete_data = {
            'delete_confirmed': True,
            'Authorization:': 'Bearer ' + access,
            'refresh': refresh
        }
        delete_response = self.client.post(delete_url, delete_data, format='json')
        self.assertEqual(delete_response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(delete_response.data['deleted'], True)
        self.assertEqual(BlacklistedToken.objects.all().count(), 1)  # make sure the token is blacklisted
        self.assertEqual(user.is_active, False)  # make sure user is inactive
        print('Done.....')

    def test_user_cannot_delete_unconfirmed(self):
        '''
        Ensure that the keyword argument 'delete_confirmed' is included in the request.
        '''
        print('Testing user cannot delete without confirming')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')  # register, login and verify user
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        delete_url = reverse('user-delete')
        delete_data = {'delete_confirmed': False}  # make sure delete_confirmed=True is required
        delete_response = self.client.post(delete_url, delete_data, format='json')
        self.assertEqual(delete_response.status_code, HTTP_400_BAD_REQUEST) # make sure request failed
        self.assertEqual(delete_response.data['deleted'], False)
        print('Done.....')

    def test_user_cannot_delete_unauthenticated(self):
        '''
        Ensure that an unauthenticated user cannot delete account.
        '''
        print('Testing user cannnot delete unauthenticated')
        delete_url = reverse('user-delete')
        delete_data = {'delete_confirmed': True}  # make sure authenticated user, refresh token and 
        delete_response = self.client.post(delete_url, delete_data, format='json')  # delete_confirmed=True required
        self.assertEqual(delete_response.status_code, HTTP_403_FORBIDDEN)
        print('Done.....')

    def test_user_can_logout_and_token_blacklisted(self):
        '''
        Ensure that the user can log out and his refresh tokens are blacklisted.
        '''
        print('Testing user can logout and his token is blacklisted')

        register_url = reverse('user-register')
        login_url = reverse('user-login')
        logout_url = reverse('user-logout')

        response = self.client.post(register_url, self.user_data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()

        login_data = {
            'username': self.user_data['username'],
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, HTTP_200_OK)

        user = User.objects.latest('created_at')
        refresh = OutstandingToken.objects.latest('created_at').token
        
        logout_data = {
            'refresh': refresh
        }

        logout_response = self.client.post(logout_url, logout_data, format='json')
        self.assertEqual(logout_response.status_code, HTTP_204_NO_CONTENT)

        self.assertEqual(BlacklistedToken.objects.all().count(), 1)

        print('Done.....')
