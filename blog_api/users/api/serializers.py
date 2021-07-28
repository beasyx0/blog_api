from rest_framework.serializers import Serializer, ModelSerializer, ValidationError, CharField, EmailField, PrimaryKeyRelatedField, SerializerMethodField
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import PasswordField

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.validators import UnicodeUsernameValidator

from blog_api.users.model_validators import validate_username_max_3_special_chars, validate_name_no_special_chars

from blog_api.users.models import UserFollowing
from blog_api.posts.models import Post
from blog_api.posts.api.serializers import PostSerializer

User = get_user_model()


class TokenObtainSerializer(Serializer):
    '''
    --Base login serializer override from https://tinyurl.com/DRFSimplejwt--
    1) Checks wether to use `email` or `username` for login.
    2) Defines default error messages
    3) Initializes self with username and password fields, uses whatever is defined
       as username_field from step # 1.
    4) Calls validate().
    '''
    username_field = settings.SIMPLE_JWT_LOGIN_USERNAME_FIELD  # 1
    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials',  # 2
        'no_user_found': 'No user found with the given credentials'
    }

    def __init__(self, *args, **kwargs):  # 3
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = CharField()
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        '''
        --Validate function--
        :returns: dict.
        1) Defines authentication keyword args to be used for authentication.
        2) Checks that a user object exists for the given credentials. Uses settings.SIMPLE_JWT_LOGIN_USERNAME_FIELD 
           to lookup user. If no user returns AuthenticationFailed 404.
        3) Attempts to add the request object to the authenticaton keyword args from # 1. If error then pass.
        4) Defines self.user by calling authenticate with the authentication keyword args from # 1.
        5) Checks that all essential setting are defined. If not returns AuthenticationFailed 400.
        6) Fallback in case we haven`t overridden get_token method. Returns NotImplementedError.
        '''
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],  # 1
            'password': attrs['password'],
        }

        try:
            if self.username_field == 'email':
                user = get_user_model().objects.get(email=authenticate_kwargs[self.username_field])  # 2
            else:
                user = get_user_model().objects.get(username=authenticate_kwargs[self.username_field])  # 2

            # make sure username is still in there, we didn't change default login field
            authenticate_kwargs['username'] = user.username

            try:
                authenticate_kwargs['request'] = self.context['request']  # 3
            except KeyError:
                pass

            self.user = authenticate(**authenticate_kwargs)  # 4

            if not api_settings.USER_AUTHENTICATION_RULE(self.user):  # 5
                raise AuthenticationFailed(
                    self.error_messages['no_active_account'],
                    'no_active_account',
                )

            return {}

        except User.DoesNotExist:
            raise AuthenticationFailed(
                    self.error_messages['no_user_found'],
                    'no_user_found',
            )

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')  # 6


class TokenObtainPairSerializer(TokenObtainSerializer):
    '''
    --Login serializer override from https://tinyurl.com/DRFSimplejwt2--
    '''
    @classmethod
    def get_token(cls, user):
        '''
        Overrides the fallback `get_token` from https://tinyurl.com/DRFSimplejwt. Returns a new token for user.
        '''
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        '''
        :returns: dict
        1) Super override validate function from same function as above.
        2) Calls get_token and assigns it to the refresh variable.
        3) Adds both new tokens to the response data.
        4) Updates last login based off jwt_settings.UPDATE_LAST_LOGIN
        '''
        data = super().validate(attrs)  # 1

        refresh = self.get_token(self.user)  # 2

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)  # 3

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)  # 4

        return data


class RegisterSerializer(ModelSerializer):
    '''
    --Register Serializer--
    '''
    username = CharField(
        required=True, 
        validators=[
            validate_username_max_3_special_chars,
            UnicodeUsernameValidator(), 
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    name = CharField(
        allow_blank=True, 
        allow_null=True, 
        max_length=255, 
        required=False, 
        validators=[validate_name_no_special_chars]
    )
    email = EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = CharField(write_only=True, required=True, validators=[validate_password])
    password2 = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'password', 'password2',)

    def validate(self, attrs):
        '''
        --Validate override--
        1) Checks to make sure both passwords match. Returns attribute dict or ValidationError.
        '''
        if not attrs['password'] == attrs['password2']:
            raise ValidationError({"password": "Password fields didn't match."})  # 1

        return attrs

    def create(self, validated_data):
        '''
        --Create function override--
        :returns: User object.
        1) Creates new user with validated data.
        2) Sets password for the new user.
        3) Saves and returns user.
        '''
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user  # 3


class UserSerializer(ModelSerializer):
    follow_counts = SerializerMethodField()
    post_count = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'pub_id', 'username', 'name', 'email', 'post_count', 'follow_counts', 'date_joined', 
        ]

    def get_post_count(self, obj):
        return obj.get_post_count()

    def get_follow_counts(self, obj):
        return obj.get_following_follower_count()


class UpdateUserSerializer(ModelSerializer):

    username = CharField(
        required=True, 
        validators=[
            validate_username_max_3_special_chars,
            UnicodeUsernameValidator(), 
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    name = CharField(
        allow_blank=True, 
        allow_null=True, 
        max_length=255, 
        required=False, 
        validators=[validate_name_no_special_chars])
    
    class Meta:
        model = User
        fields = ('username', 'name',)


class UserFollowingSerializer(ModelSerializer):

    following_username = SerializerMethodField()

    class Meta:
        model = UserFollowing
        fields = ('following', 'following_username',)

    def get_following_username(self, obj):
        return obj.following.username


class UserFollowersSerializer(ModelSerializer):

    follower = SerializerMethodField()
    follower_username = SerializerMethodField()

    class Meta:
        model = UserFollowing
        fields = ('follower', 'follower_username',)

    def get_follower(self, obj):
        return obj.user.pub_id

    def get_follower_username(self, obj):
        return obj.user.username
