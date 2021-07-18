import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    '''Base model to subclass.'''
    created_at = models.DateTimeField(editable=False, null=True)
    updated_at = models.DateTimeField(editable=False, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(BaseModel, self).save(*args, **kwargs)


class User(BaseModel, AbstractUser):
    '''User model. New users are inactive until verified through email'''
    pub_id = models.CharField(editable=False, unique=True, max_length=50)
    name = models.CharField(blank=True, max_length=255)
    email = models.EmailField(unique=True, blank=False, max_length=254)
    first_name = None
    last_name = None
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        '''
        --User model save method--
        1) Sets self.pub_id to UUID hex on first save.
        '''
        if not self.id:
            self.pub_id = str(uuid.uuid4().hex)
        return super(User, self).save(*args, **kwargs)


class VerificationCode(BaseModel):
    '''Verification Code model. Code is sent to user for verification, users are inactive until verified'''
    verification_code = models.CharField(editable=False, unique=True, max_length=50)
    user_to_verify = models.ForeignKey(User, related_name='verification_codes', on_delete=models.CASCADE)
    code_expiration = models.DateTimeField(default=timezone.now() + timedelta(days=3))
    is_verified = models.BooleanField(default=False)

    def send_user_verification_email(self):

        '''
        --Send user verification email--
        Sends user a verification code email using user.email_user(), the link sent
        points to settings.FRONTEND_URL. If code is expired user is deleted.
        '''
        now = timezone.now()
        user = self.user_to_verify
        if not (self.code_expiration >= now):
            user.delete()
            return {
                'verification_sent': False,
                'message': 'Code expired, please re-register first then check your email.'
            }
        subject = f'{user.username}, please verify your email'
        template = 'email_templates/verification_email.txt'
        html_template = 'email_templates/verification_email.html'
        message_data = {
            'url': settings.FRONTEND_URL + str(self.verification_code) + '/'
        }
        message = render_to_string(template, message_data)
        html_message = render_to_string(html_template, message_data)
        from_email = (
            'verification@' + settings.FRONTEND_URL.split('.')[-2] + '.com'
        )
        user.email_user(subject=subject, message=message, html_message=html_message, from_email=from_email)
        return {
            'verification_sent': True,
            'message': 'Verification code sent! Check your email.'
        }

    def verify(self):
        '''
        --Code verification--
        :returns: dict
        1) Checks that the code has not expired. If so returns verified False.
        2) Checks if the code has already been verified. If so returns verified True.
        3) Updates self to verified and sets the user to active. Returns veified True.
        '''
        now = timezone.now()
        if not (self.code_expiration >= now):  # 1
            self.user_to_verify.delete()
            return {
                'verified': False,
                'message': 'Code expired, please re-register first then check your email'
            }
        elif (self.is_verified == True):  # 2
            return {
                'verified': True,
                'message': 'Code is already verified, please log in.'
            }
        else:
            self.is_verified = True
            self.user_to_verify.is_active = True  # 3 this needs to expire the code
            self.save()
            self.user_to_verify.save()
            return {
                'verified': True,
                'message': 'Code verified and the user is now active! You may now log in.'
            }

    class Meta:
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'

    def __str__(self):
        return str(self.verification_code)

    def save(self, *args, **kwargs):
        '''
        --VerificationCode model save method--
        1) Sets self.verification_code to UUID hex on first save.
        '''
        if not self.id:
            self.verification_code = str(uuid.uuid4().hex)  # 1
        return super(VerificationCode, self).save(*args, **kwargs)


class PasswordResetCode(BaseModel):
    '''
    --Password reset link--
    '''
    user = models.ForeignKey(User, related_name='password_reset_links', on_delete=models.CASCADE)
    password_reset_code = models.CharField(editable=False, unique=True, max_length=50)
    code_expiration = models.DateTimeField(default=timezone.now() + timedelta(days=3))

    def send_user_password_reset_email(self):
        '''
        --Send user password reset email--
        1) Send user a link to the frontend with a code that will let them post back to another url 
           with updated passwords.
        '''
        now = timezone.now()
        user = self.user
        if not (self.code_expiration >= now):
            return {
                'password_reset_link_sent': False,
                'message': 'Password reset link expired.'
            }
        subject = f'{user.username}, here is the link to reset your password.'
        template = 'email_templates/password_reset_link_email.txt'
        html_template = 'email_templates/password_reset_link_email.html'
        message_data = {
            'url': settings.FRONTEND_URL + 'password/reset/' + self.password_reset_code + '/'
        }
        message = render_to_string(template, message_data)
        html_message = render_to_string(html_template, message_data)
        from_email = (
            'password-reset@' + settings.FRONTEND_URL.split('.')[-2] + '.com/'
        )
        user.email_user(subject=subject, message=message, html_message=html_message, from_email=from_email)

        return {
            'password_reset_link_sent': True,
            'message': 'Password reset link sent! Check your email.'
        }

    def __str__(self):
        return str(self.password_reset_code)

    def save(self, *args, **kwargs):
        '''
        --PasswordResetLink model save method--
        1) Sets self.pub_id to UUID hex on first save.
        '''
        if not self.id:
            self.password_reset_code = str(uuid.uuid4().hex)
        return super(PasswordResetCode, self).save(*args, **kwargs)

