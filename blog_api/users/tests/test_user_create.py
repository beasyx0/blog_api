from datetime import timedelta
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
                                                                        HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from blog_api.users.models import User, VerificationCode, PasswordResetCode


class UserTestsCreate(APITestCase):

    def setUp(self):
        self.user_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user2_dif_email_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail00@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user3_dif_username_data = {
            'name': 'DabApps',
            'username': 'someuser0000',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user4_no_name_data = {
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user5_no_username_data = {
            'name': 'DabApps',
            'username': '',
            'email': 'someemail@email.com',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user6_no_email_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': '',
            'password': 'Testing4321@',
            'password2': 'Testing4321@'
        }
        self.user7_only_1_pass_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': '',
            'password2': 'Testing4321@'
        }
        self.user8_no_secure_pass_data = {
            'name': 'DabApps',
            'username': 'someuser00',
            'email': 'someemail@email.com',
            'password': 'kjkkjllll',
            'password2': 'kjkkjllll'
        }

    def test_user_register_new_account(self):
        """
        Ensure we can create a new user and that the user is_active == False,
        that BaseModel saved correctly, a new VerificationCode is
        created and user ip recorded.
        """
        print('Testing registering new user')
        register_url = reverse('user-register')
        now = timezone.now()
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        self.assertEqual(response.data['message'], 'User registered successfully, please check your email to verify.')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, 'DabApps')
        self.assertEqual(User.objects.last().is_active, False)
        self.assertEqual(User.objects.last().created_at.date(), now.date())
        self.assertEqual(User.objects.last().updated_at.date(), now.date())
        self.assertNotEqual(User.objects.last().ip_address, None)
        self.assertEqual(VerificationCode.objects.count(), 1)
        print('Done.....')

    def test_user_register_new_account_name_not_required(self):
        """
        Ensure we can create a new user without providing a name and that the name is set to email name,
        the user is_active == False, the BaseModel saved correctly and that a new VerificationCode is created and emailed.
        """
        print('Testing registering new user without name')
        register_url = reverse('user-register')
        now = timezone.now()
        response = self.client.post(register_url, self.user4_no_name_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, self.user4_no_name_data['email'].split('@')[0])  # default is email name
        self.assertEqual(User.objects.last().is_active, False)
        self.assertEqual(User.objects.last().created_at.date(), now.date())
        self.assertEqual(User.objects.last().updated_at.date(), now.date())
        self.assertEqual(VerificationCode.objects.count(), 1)
        print('Done.....')

    def test_user_register_new_account_fails_email_already_exists(self):
        """
        Ensure that we return the appropriate message if a user tries to register when already having account.
        """
        print('Testing registering new user email already exists')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        response2 = self.client.post(register_url, self.user3_dif_username_data, format='json')
        self.assertEqual(response2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['registered'], False)
        self.assertEqual(
            response2.data['message'], 
            'A user with those credentials already exists and is inactive. Verification code sent! Check your email.'
        )
        
        verificaton_data = {'verification_code': VerificationCode.objects.last().verification_code}
        self.client.post(verification_url, verificaton_data, format='json')  # verify user
        
        response3 = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response3.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.data['registered'], False)
        self.assertEqual(
            response3.data.get('message'), 
            'The user is already verified and active. Please log in.'
        )
        print('Done.....')

    def test_user_register_new_account_fails_username_already_exists(self):
        """
        Ensure that we return the appropriate message if a user tries to register when already having account.
        """
        print('Testing registering new user username already exists')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        
        response2 = self.client.post(register_url, self.user2_dif_email_data, format='json')
        self.assertEqual(response2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['registered'], False)
        self.assertEqual(
            response2.data.get('message'), 
            'A user with those credentials already exists and is inactive. Verification code sent! Check your email.'
        )
        
        verificaton_data = {'verification_code': VerificationCode.objects.last().verification_code}
        self.client.post(verification_url, verificaton_data, format='json')
        
        response3 = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response3.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.data['registered'], False)
        self.assertEqual(
            response3.data.get('message'), 
            'The user is already verified and active. Please log in.'
        )
        print('Done.....')

    def test_user_register_new_account_fails_while_already_registered_account_is_inactive(self):
        print('Testing registering new user while already registered and account is inactive')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        response2 = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['registered'], False)
        self.assertEqual(
            response2.data['message'], 
            'A user with those credentials already exists and is inactive. Verification code sent! Check your email.'
        )

    def test_user_register_new_account_fails_with_no_username(self):
        """
        Ensure that username is required, registering fails when creating new user and
        no VerificationCode object is created.
        """
        print('Testing registering new user without username')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user5_no_username_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(VerificationCode.objects.count(), 0)
        print('Done.....')

    def test_user_register_new_account_fails_with_no_email(self):
        """
        Ensure that email is required and registering fails when creating new user and
        no VerificationCode object is created.
        """
        print('Testing registering new user without email')

        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user6_no_email_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(VerificationCode.objects.count(), 0)
        print('Done.....')

    def test_user_register_new_account_fails_without_both_passwords(self):
        """
        Ensure that both passwords are required and registering fails when creating new user and
        no VerificationCode object is created.
        """
        print('Testing registering new user without both passwords')

        register_url = reverse('user-register')
        
        response = self.client.post(register_url, self.user7_only_1_pass_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(VerificationCode.objects.count(), 0)
        print('Done.....')

    def test_user_register_new_account_fails_password_not_secure(self):
        '''
        Ensure that registering new user fails with insecure password.
        '''
        print('Testing registering new user without secure password')

        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user8_no_secure_pass_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(VerificationCode.objects.count(), 0)
        print('Done.....')

    def test_user_register_new_account_fails_already_registered_and_active(self):
        '''
        Ensure that a user that is already registered and active cannot register and recieves a message and .
        '''
        print('Testing registering new user email already exists')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        
        verificaton_data = {'verification_code': VerificationCode.objects.latest('created_at').verification_code}
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(verification_response.data['message'], 'Code verified and the user is now active! You may now log in.')
        
        response2 = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['registered'], False)
        self.assertEqual(
            response2.data['message'], 
            'The user is already verified and active. Please log in.'
        )
        print('Done.....')

    def test_user_register_new_account_fails_username_more_than_3_special_chars(self):
        """
        Ensure that we return the appropriate message if a user tries to register with more than 3 special chars in username.
        """
        print('Testing registering new user fails with more than 3 special characters in username')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        self.user_data['username'] = 'billy@@@@'

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)

        print('Done.....')

    def test_user_register_new_account_fails_name_with_special_chars(self):
        """
        Ensure that we return the appropriate message if a user tries to register with special characters in name.
        """
        print('Testing registering new user fails with special characters in name')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        self.user_data['name'] = 'billy@@@@'

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)

        print('Done.....')

    def test_user_register_new_account_fails_username_with_spaces(self):
        """
        Ensure that we return the appropriate message if a user tries to register with spaces in username.
        """
        print('Testing registering new user fails with spaces in username')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        self.user_data['username'] = 'bill y@@'

        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['registered'], False)

        print('Done.....')

    def test_user_verify(self):
        print('Testing new user can verify')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        
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
        print('Done.....')

    def test_user_verify_fails_wrong_code(self):
        print('Testing new user cannot verify with wrong code')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': 'kkjjjjy767gy6'
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(verification_response.data['verified'], False)
        self.assertEqual(verification_response.data['message'], 'No verification code found with provided code.')
        print('Done.....')

    def test_user_resend_verification_email(self):
        """
        Ensure we can resend the verification email
        """
        print('Testing can resend verification email')
        register_url = reverse('user-register')
        verify_resend_url = reverse('user-verify-resend')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        
        resend_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(resend_response.status_code, HTTP_200_OK)
        self.assertEqual(resend_response.data['verifification_sent'], True)
        self.assertEqual(len(mail.outbox), 1)
        
        print('Done.....')

    def test_user_resend_verification_email_fails_user_already_active(self):
        '''
        Ensure if an active user tries to resend the verification email it fails with a message.
        '''
        print('Testing cannot resend verification email user already active')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        verify_resend_url = reverse('user-verify-resend')
        
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

        resend_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(resend_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(resend_response.data['verifification_sent'], False)
        self.assertEqual(resend_response.data['message'], 'The user is already verified and active. Please log in.')
        self.assertEqual(len(mail.outbox), 0)
        
        print('Done.....')

    def test_user_resend_verification_email_fails_no_password(self):
        '''
        Ensure that the user cannot resend the verification email without the correct password.
        '''
        print('Testing cannot resend verification email no password')
        register_url = reverse('user-register')
        verify_resend_url = reverse('user-verify-resend')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        resend_data = {
            'email': self.user_data['email'],
            'password': ''
        }
        resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(resend_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(resend_response.data['verifification_sent'], False)
        self.assertEqual(len(mail.outbox), 0)

    def test_user_resend_verification_email_fails_no_email(self):
        '''
        Ensure that the user cannot resend the verification email without a valid email.
        '''
        print('Testing cannot resend verification email no email')
        register_url = reverse('user-register')
        verify_resend_url = reverse('user-verify-resend')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)

        resend_data = {
            'email': '',
            'password': self.user_data['password']
        }
        resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(resend_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(resend_response.data['verifification_sent'], False)
        self.assertEqual(len(mail.outbox), 0)

    def test_user_resend_verification_email_expired_resends_new_verification(self):
        """
        Ensure the user recieves new verification email with new code and expiration if he tries to 
        resend the verification email while code is expired.
        """
        print('Testing expired verification gets resent with no code and expiration')
        register_url = reverse('user-register')
        verify_resend_url = reverse('user-verify-resend')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        
        resend_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(resend_response.status_code, HTTP_200_OK)
        self.assertEqual(resend_response.data['verifification_sent'], True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(resend_response.data['message'], 'Verification code sent! Check your email.')

        verification_code = VerificationCode.objects.latest('created_at')
        verification_code.code_expiration = verification_code.code_expiration - timedelta(days=30)
        verification_code.save()

        now_day = (timezone.now() + timedelta(days=3)).day
        expired_resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(expired_resend_response.status_code, HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(expired_resend_response.data['message'], 'Verification code sent! Check your email.')
        verification_code.refresh_from_db()
        self.assertEqual(now_day, verification_code.code_expiration.day)

        print('Done.....')

    def test_user_send_password_reset_link(self):
        '''
        Ensure that the user can submit his email and get a link sent with password reset instructions.
        '''
        print('Testing new user can submit get password reset link.')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        password_reset_send_url = reverse('user-password-reset-send')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')


        print('Done.....')

    def test_user_send_password_reset_link_expired_resends_new_password_reset_link(self):
        '''
        Ensure that a user recieves a new password reset link in his email with a new code and expiration if he 
        tries to get one and one already exist.
        '''
        print('Testing user recieves new password reset link with new code and expiration if one exists and is expired')
        register_url = reverse('user-register')
        password_resend_url = reverse('user-password-reset-send')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        
        resend_data = {
            'email': self.user_data['email'],
        }
        resend_response = self.client.post(password_resend_url, resend_data)
        self.assertEqual(resend_response.status_code, HTTP_200_OK)
        self.assertEqual(resend_response.data['password_reset_link_sent'], True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(resend_response.data['message'], 'Password reset link sent! Check your email.')

        password_reset_code = PasswordResetCode.objects.latest('created_at')
        password_reset_code.code_expiration = password_reset_code.code_expiration - timedelta(days=30)
        password_reset_code.save()

        now_day = (timezone.now() + timedelta(days=3)).day
        expired_resend_response = self.client.post(password_resend_url, resend_data)
        self.assertEqual(expired_resend_response.status_code, HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(expired_resend_response.data['message'], 'Password reset link sent! Check your email.')
        password_reset_code.refresh_from_db()
        self.assertEqual(now_day, password_reset_code.code_expiration.day)

        print('Done.....')

    def test_user_can_reset_password(self):
        print('Testing user can reset password')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        password_reset_send_url = reverse('user-password-reset-send')
        password_reset_url = reverse('user-password-reset')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')

        code = PasswordResetCode.objects.latest('created_at')
        password_reset_data = {
            'password_reset_code': code.password_reset_code,
            'password': 'Newpass9@',
            'password2': 'Newpass9@'
        }
        password_reset_response = self.client.post(password_reset_url, password_reset_data, format='json')
        self.assertEqual(password_reset_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_response.data['password_reset'], True)
        self.assertEqual(password_reset_response.data['message'], 'The password has been reset. Please continue to log in.')

        print('Done.....')

    def test_user_reset_password_fails_not_email(self):
        '''
        Ensure the send reset password requires an email.
        '''
        print('Testing user send password reset fails without email')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        password_reset_send_url = reverse('user-password-reset-send')
        password_reset_url = reverse('user-password-reset')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        password_reset_send_data = {'email': ''}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], False)
        self.assertEqual(password_reset_send_response.data['message'], 'Please post a valid email to get reset password link.')

        print('Done.....')

    def test_user_reset_password_fails_non_matching_passwords(self):
        print('Testing user cannot reset password without matching passwords')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        password_reset_send_url = reverse('user-password-reset-send')
        password_reset_url = reverse('user-password-reset')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')

        code = PasswordResetCode.objects.latest('created_at')
        password_reset_data = {
            'password_reset_code': code.password_reset_code,
            'password': 'Testing2',
            'password2': 'Testing7'
        }
        password_reset_response = self.client.post(password_reset_url, password_reset_data, format='json')
        self.assertEqual(password_reset_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(password_reset_response.data['password_reset'], False)
        self.assertEqual(password_reset_response.data['message'], 'Please post matching passwords to reset password.')

        print('Done.....')

    def test_user_reset_password_fails_password_not_secure(self):
        print('Testing user cannot reset password not secure')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        password_reset_send_url = reverse('user-password-reset-send')
        password_reset_url = reverse('user-password-reset')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')

        code = PasswordResetCode.objects.latest('created_at')
        password_reset_data = {
            'password_reset_code': code.password_reset_code,
            'password': 'testingg',
            'password2': 'testingg'
        }
        password_reset_response = self.client.post(password_reset_url, password_reset_data, format='json')
        self.assertEqual(password_reset_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(password_reset_response.data['password_reset'], False)
        self.assertEqual(
            password_reset_response.data['message'], 
            'The password is not valid. Please choose one that is more secure.'
        )

        print('Done.....')

    def test_user_can_login_just_email(self):
        print('Testing new user can login just email')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        self.client.post(verification_url, verificaton_data, format='json')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_200_OK)
        print('Done.....')

    def test_user_cannot_login_not_verified(self):
        print('Testing new user cannot login not verified')
        register_url = reverse('user-register')
        login_url = reverse('user-login')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_401_UNAUTHORIZED)
        print('Done.....')

    def test_user_cannot_login_wrong_email(self):
        print('Testing new user cannot login wrong email')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        login_data = {
            'email': 'kjl' + self.user_data['email'],
            'password': self.user_data['password']
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_401_UNAUTHORIZED)
        print('Done.....')

    def test_user_cannot_login_wrong_password(self):
        print('Testing new user cannot login wrong password')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        login_url = reverse('user-login')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.latest('created_at').verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)

        login_data = {
            'email': self.user_data['email'],
            'password': 'khkj'
        }
        new_login = self.client.post(login_url, login_data, format='json')
        self.assertEqual(new_login.status_code, HTTP_401_UNAUTHORIZED)
        print('Done.....')
