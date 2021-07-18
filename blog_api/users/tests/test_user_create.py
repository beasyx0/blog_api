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
            'name': '',
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
        that BaseModel saved correctly and that a new VerificationCode is
        created.
        """
        print('Testing registering new user')
        url = reverse('user-register')
        now = timezone.now()
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        self.assertEqual(response.data['message'], 'User registered successfully, please check your email to verify.')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, 'DabApps')
        self.assertEqual(User.objects.last().is_active, False)
        self.assertEqual(User.objects.last().created_at.date(), now.date())
        self.assertEqual(User.objects.last().updated_at.date(), now.date())
        self.assertEqual(VerificationCode.objects.count(), 1)
        print('Done.....')

    def test_user_register_new_account_email_already_exists(self):
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
            response2.data.get('message'), 
            'An account for that user already exists and is inactive. Please try to resend verification email to reactivate.'
        )
        
        verificaton_data = {'verification_code': VerificationCode.objects.last().verification_code}
        self.client.post(verification_url, verificaton_data, format='json')  # verify user
        
        response3 = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response3.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.data['registered'], False)
        self.assertEqual(
            response3.data.get('message'), 
            'An account for that user already exists and is active. Please try to login or reset password.'
        )
        print('Done.....')

    def test_user_register_new_account_username_already_exists(self):
        """
        Ensure that we return the appropriate message if a user tries to register when already having account.
        """
        print('Testing registering new user username already exists')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')

        response = self.client.post(register_url, self.user_data, format='json')  # register new user
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        
        response2 = self.client.post(register_url, self.user2_dif_email_data, format='json')  # attempt to register same user again different email same username
        self.assertEqual(response2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['registered'], False)
        self.assertEqual(
            response2.data.get('message'), 
            'An account for that user already exists and is inactive. Please try to resend verification email to reactivate.'
        )
        
        verificaton_data = {'verification_code': VerificationCode.objects.last().verification_code}  # verify user
        self.client.post(verification_url, verificaton_data, format='json')
        
        response3 = self.client.post(register_url, self.user_data, format='json')  # attempt to register same user again after verified
        self.assertEqual(response3.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.data['registered'], False)
        self.assertEqual(
            response3.data.get('message'), 
            'An account for that user already exists and is active. Please try to login or reset password.'  # email exist user active
        )
        print('Done.....')

    def test_user_register_new_account_while_already_registered_account_is_inactive(self):
        print('Testing registering new user while already registered and account is inactive')
        register_url = reverse('user-register')
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        response2 = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data['registered'], False)
        self.assertEqual(response2.data['message'], 'An account for that user already exists and is inactive. Please try to resend verification email to reactivate.')

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
        self.assertEqual(User.objects.get().name, 'someemail')  # default is email name
        self.assertEqual(User.objects.last().is_active, False)
        self.assertEqual(User.objects.last().created_at.date(), now.date())
        self.assertEqual(User.objects.last().updated_at.date(), now.date())
        self.assertEqual(VerificationCode.objects.count(), 1)
        print('Done.....')

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

    def test_user_verify(self):
        print('Testing new user can verify')
        register_url = reverse('user-register')
        verification_url = reverse('user-verify')
        
        response = self.client.post(register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['registered'], True)
        verificaton_data = {
            'verification_code': VerificationCode.objects.last().verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(verification_response.data['message'], 'Code verified and the user is now active! You may now log in.')
        self.assertEqual(VerificationCode.objects.last().is_verified, True)
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

    def test_user_resend_verification_email_fails_expired_and_deletes_user(self):
        """
        Ensure we cannot resend the verification email if it's expired. Also ensure the user is deleted and told to re-register
        """
        print('Testing cannot resend verification email when its expired and that user is deleted')
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

        verification_code = VerificationCode.objects.last()
        verification_code.code_expiration = verification_code.code_expiration - timedelta(days=30)
        verification_code.save()

        expired_resend_response = self.client.post(verify_resend_url, resend_data)
        self.assertEqual(expired_resend_response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(expired_resend_response.data['verifification_sent'], False)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertEqual(expired_resend_response.data['message'], 'Code expired, please re-register first then check your email.')

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
            'verification_code': VerificationCode.objects.last().verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(VerificationCode.objects.last().is_verified, True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')


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
            'verification_code': VerificationCode.objects.last().verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(VerificationCode.objects.last().is_verified, True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')

        code = PasswordResetCode.objects.last()
        password_reset_data = {
            'password_reset_code': code.password_reset_code,
            'password': 'Newpass9@',
            'password2': 'Newpass9@'
        }
        password_reset_response = self.client.post(password_reset_url, password_reset_data, format='json')
        self.assertEqual(password_reset_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_response.data['password_reset'], True)
        self.assertEqual(password_reset_response.data['message'], 'Password reset! Please continue to login.')

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
            'verification_code': VerificationCode.objects.last().verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(VerificationCode.objects.last().is_verified, True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')

        code = PasswordResetCode.objects.last()
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
            'verification_code': VerificationCode.objects.last().verification_code
        }
        verification_response = self.client.post(verification_url, verificaton_data, format='json')
        self.assertEqual(verification_response.status_code, HTTP_200_OK)
        self.assertEqual(verification_response.data['verified'], True)
        self.assertEqual(VerificationCode.objects.last().is_verified, True)

        password_reset_send_data = {'email': self.user_data['email']}
        password_reset_send_response = self.client.post(password_reset_send_url, password_reset_send_data)
        self.assertEqual(password_reset_send_response.status_code, HTTP_200_OK)
        self.assertEqual(password_reset_send_response.data['password_reset_link_sent'], True)
        self.assertEqual(password_reset_send_response.data['message'], 'Password reset link sent! Check your email.')

        code = PasswordResetCode.objects.last()
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
            'Please make sure your passwords match, are at least 8 characters long, include a number and is not too common.'
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
            'verification_code': VerificationCode.objects.last().verification_code
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
        verification_url = reverse('user-verify-resend')
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
