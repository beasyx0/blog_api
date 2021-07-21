from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from django.urls import reverse

from blog_api.users.models import User, VerificationCode


class UserTestsRead(APITestCase):

    # READ
    def test_user_can_get_user_authenticated(self):
        '''
        Ensure an authenticated user can view his data.
        '''
        register_url = reverse('user-register')
        data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        response = self.client.post(register_url, data, format='json')
        user = User.objects.latest('created_at')
        vcode = VerificationCode.objects.latest('created_at')
        vcode.verify()
        self.client.force_login(user=user)
        response = self.client.get(reverse("user"))
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_user_cannot_get_user_unauthenticated(self):
        '''
        Ensure an unauthenticated user cannot view his data.
        '''
        response = self.client.get(reverse("user"))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
