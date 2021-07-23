import uuid
from datetime import timedelta
from django.conf import settings
from django.db.models import Model, Manager, DateTimeField, CharField, EmailField, BooleanField, \
                                                        GenericIPAddressField, ForeignKey, CASCADE, UniqueConstraint
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator

from blog_api.users.model_validators import validate_username_min_3_letters, validate_username_max_3_special_chars, \
                                                                                            validate_name_no_special_chars


class BaseModel(Model):
    '''Base model to subclass.'''
    created_at = DateTimeField(editable=False, null=True)
    updated_at = DateTimeField(editable=False, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(BaseModel, self).save(*args, **kwargs)


class User(BaseModel, AbstractUser):
    '''User model. New users are inactive until verified through email'''
    pub_id = CharField(editable=False, unique=True, max_length=50)
    username = CharField(
        max_length=150, unique=True, 
        validators=[
            UnicodeUsernameValidator, validate_username_min_3_letters, validate_username_max_3_special_chars
        ]
    )
    name = CharField(blank=True, null=True, max_length=255, validators=[validate_name_no_special_chars])
    email = EmailField(unique=True, blank=False, null=False, max_length=254)
    first_name = None
    last_name = None
    is_active = BooleanField(default=False)
    ip_address = GenericIPAddressField(editable=False, blank=True, null=True)

    def password_reset(self, password):
        try:
            validate_password(password, self)
        except ValidationError:
            return {
                'password_reset': False,
                'message': 'The password is not valid. Please choose one that is more secure.'
            }
        self.set_password(password)
        self.save()

        password_reset_codes_exist = self.password_reset_codes.all().exists()
        if password_reset_codes_exist:
            now = timezone.now()
            for code in self.password_reset_codes.all():
                code.code_expiration = (now - timedelta(days=100))
                code.save()

        return {
            'password_reset': True,
            'message': 'The password has been reset. Please continue to log in.'
        }

    def follow_user(self, pubid):
        '''
        Follow or unfollow a user based on if follow exists already.
        '''
        if not User.objects.filter(pub_id=pubid).exists():
            return {
                'followed': False,
                'message': 'No user found with provided id.'
            }
        user_to_follow = User.objects.get(pub_id=pubid)
        if not UserFollowing.objects.filter(user=self, following=user_to_follow).exists():
            follow = UserFollowing.objects.create(user=self, following=user_to_follow)
            return {
                'followed': True,
                'message': f'{user_to_follow.username} followed successfully.'
            }
        else:
            UserFollowing.objects.filter(user=self, following=user_to_follow).delete()
            return {
                'followed': False,
                'message': f'{user_to_follow.username} unfollowed successfully.'
            }

    def get_following(self):
        '''
        Return a dictionary of the users a user is following.
        '''
        self_followings = self.following.all()
        following = []
        for follow in self_followings:
            following.append({'pub_id': follow.following.pub_id, 'username': follow.following.username})
        return following

    def get_following_posts(self):
        '''
        Get all posts of those the user is following.
        '''
        from blog_api.posts.models import Post
        following_posts = []
        for follow in self.following.all():
            posts = Post.objects.filter(author=follow.following)
            for post in posts:
                following_posts.append({'slug': post.slug, 'title': post.title})
        return following_posts

    def get_followers(self):
        '''
        Return a dictionary of the users followers.
        '''
        self_followerss = self.followers.all()
        followers= []
        for follow in self_followerss:
            followers.append({'pub_id': follow.user.pub_id, 'username': follow.user.username})
        return followers

    def get_posts(self):
        '''
        Return all posts by this user.
        '''
        from blog_api.posts.models import Post  # avoid import errors
        self_posts = Post.objects.filter(author=self)
        posts = []
        for post in self_posts:
            posts.append({'slug': post.slug, 'title': post.title})
        return posts

    def bookmark_post(self, slug):
        '''
        Bookmarks a post for this user.
        '''
        from blog_api.posts.models import Post
        try:
            post_to_bookmark = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return {
                'bookmarked': False,
                'message': 'No post found with provided slug.'
            }
        bookmarked = post_to_bookmark.bookmark(pubid=self.pub_id)
        return bookmarked

    def get_self_bookmarks(self):
        '''
        Return all bookmarked posts for this user
        '''
        from blog_api.posts.models import Post  # avoid import errors
        bookmarked_posts = Post.objects.filter(bookmarks__pub_id=self.pub_id)
        bookmarks = []
        for post in bookmarked_posts:
            bookmarks.append({'slug': post.slug, 'title': post.title})
        return bookmarks

    class Meta:
        ordering = ['-created_at',]

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
    verification_code = CharField(editable=False, unique=True, max_length=50)
    user_to_verify = ForeignKey(User, related_name='verification_codes', on_delete=CASCADE)
    code_expiration = DateTimeField(default=timezone.now() + timedelta(days=3))

    def send_user_verification_email(self):

        '''
        --Send user verification email--
        Sends user a verification code email using user.email_user() if the user is not active, 
        the link sent points to settings.FRONTEND_URL. If code is expired then code is rotated and
        expiration extended.
        '''
        if self.user_to_verify.is_active:
            return {
                'verification_sent': False,
                'message': 'The user is already verified and active. Please log in.'
            }
        now = timezone.now()
        if not (self.code_expiration >= now):
            self.code_expiration = now + timedelta(days=3)
            self.verification_code = str(uuid.uuid4().hex)
            self.save()

        subject = f'{self.user_to_verify.username}, please verify your email'
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
        self.user_to_verify.email_user(subject=subject, message=message, html_message=html_message, from_email=from_email)
        return {
            'verification_sent': True,
            'message': 'Verification code sent! Check your email.'
        }

    def verify(self):
        '''
        --Code verification--
        1) If the code is expired then resend verification email return False and message.
        2) Expire the code.
        3) Set user to active and return True and message.
        '''
        now = timezone.now()
        if not (self.code_expiration >= now):  # 1
            self.send_user_verification_email()
            return {
                'verified': False,
                'message': 'Code expired. Please check your email for a new verification.'
            }
        self.code_expiration = (now - timedelta(days=100))  # 2
        self.save()
        self.user_to_verify.is_active = True  # 3
        self.user_to_verify.save()  
        return {
            'verified': True,
            'message': 'Code verified and the user is now active! You may now log in.'
        }


    class Meta:
        ordering = ['-created_at']

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
    --Password reset code--
    '''
    user = ForeignKey(User, related_name='password_reset_codes', on_delete=CASCADE)
    password_reset_code = CharField(editable=False, unique=True, max_length=50)
    code_expiration = DateTimeField(default=timezone.now() + timedelta(days=3))

    def send_user_password_reset_email(self):
        '''
        --Send user password reset email--
        1) Send user a link to the frontend with a code that will let them post back to another url 
           with updated passwords. 
        '''
        now = timezone.now()
        if not (self.code_expiration >= now):
            self.code_expiration = now + timedelta(days=3)
            self.password_reset_code = str(uuid.uuid4().hex)
            self.save()

        subject = f'{self.user.username}, here is the link to reset your password.'
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
        self.user.email_user(subject=subject, message=message, html_message=html_message, from_email=from_email)
        return {
            'password_reset_link_sent': True,
            'message': 'Password reset link sent! Check your email.'
        }

    def verify(self, password):
        '''
        --Code verification--
        1) If code is expired resend password reset email.
        2) Call password_reset on user and return either True or False and a message.
        '''
        now = timezone.now()
        if not (self.code_expiration >= now):
            self.send_user_password_reset_email()  # 1
            return {
                'password_reset': False,
                'message': 'Code expired. Please check your email for a new password reset link.'
            }

        password_reset = self.user.password_reset(password)
        return {
            'password_reset': password_reset['password_reset'],
            'message': password_reset['message']
        }

    class Meta:
        ordering = ['-created_at']

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


class UserFollowing(BaseModel):

    user = ForeignKey(User, related_name='following', on_delete=CASCADE, to_field='pub_id')
    following = ForeignKey(User, related_name='followers', on_delete=CASCADE, to_field='pub_id')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user','following'],  name='unique_followers')
        ]

        ordering = ['-created_at']

    def clean(self):
        if self.user.email == self.following.email:
            raise ValidationError('You can not follow yourself.')
        return super().clean()

    def __str__(self):
        return f'{self.user.username} follows {self.following}'

    # def get_self_user_pub_id(self):
    #     return self.user.pub_id

    # def get_self_user_username(self):
    #     return self.user.username

    # def get_self_following_pub_id(self):
    #     return self.following.pub_id

    # def get_self_following_username(self):
    #     return self.following.username
