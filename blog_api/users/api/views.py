from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

from blog_api.users.api.serializers import TokenObtainPairSerializer, RegisterSerializer, UserSerializer, UserFollowingSerializer, UserFollowersSerializer
from blog_api.users.models import VerificationCode, PasswordResetCode
from blog_api.posts.models import Post, Like, DisLike
from blog_api.posts.api.serializers import PostSerializer
from blog_api.posts.api.views import get_paginated_queryset
from blog_api.users.signals import new_registration
from blog_api.users.utils import get_client_ip


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_register(request):
    '''
    --New user register view--
    ==========================================================================================================
    :param: str username (required)
    :param: str email (required)
    :param: str password (required)
    :param: str password2 (required)
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    1) Checks if the desired email or username is already taken. If so returns 400, an appropriate 
       message on wether existing user is active or not and in case inactive resends verification email.
    2) Checks if name in request is blank or none. If so adds email name as name.
    3) Attempts to serialize and save new user. Returns 201 for created 400 for errors.
    4) Record the users ip address for metrics.
    ==========================================================================================================
    '''
    user_desired_email = request.data.get('email', None)
    user_email_exists = User.objects.filter(email=user_desired_email).exists()  # 1
    
    user_desired_username = request.data.get('username', None)
    username_exists = User.objects.filter(username=user_desired_username).exists()

    if any([user_email_exists, username_exists]):
        try:
            user = User.objects.get(email=user_desired_email)
        except User.DoesNotExist:
            user = User.objects.get(username=user_desired_username)  # one of them exists

        verification = user.verification_codes.latest('created_at').send_user_verification_email()
        if verification['verification_sent']:
            return Response({
                    'registered': False,
                    'message': 'A user with those credentials already exists and is inactive. ' + verification['message']
                }, status=HTTP_400_BAD_REQUEST
            )
        else:
            return Response({
                    'registered': False,
                    'message': verification['message']
                }, status=HTTP_400_BAD_REQUEST
            )

    name = request.data.get('name', None)  # 2
    if not name or name == '':
        if user_desired_email:
            name = user_desired_email.split('@')[0]
        else:
            name = 'Awesome User'

        request.data['name'] = name

    serializer = RegisterSerializer(data=request.data)  # 3
    if serializer.is_valid():
        serializer.save()
        
        user_username = serializer.data['username']  # 4
        user_ip_address = get_client_ip(request)
        new_registration.send(
            sender='new_registration_done', ip_address=user_ip_address, user_username=user_username, task_id=299
        )
        return Response({
                'registered': True,
                'message': 'User registered successfully, please check your email to verify.'
            }, status=HTTP_201_CREATED
        )

    return Response({
            'registered': False,
            'message': serializer.errors,
        }, status=HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_verify(request):
    '''
    --User verification email view--
    ==========================================================================================================
    :param: str verification code (required).
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    1) Checks for required verification code in the request. If no code returns 400.
    2) Checks that a verification code object exists for code given. If no code then returns 400.
    3) Calls verify() on the verification code object. Returns 200 for veried == True else 400.
    ==========================================================================================================
    '''

    verification_code = request.data.get('verification_code', None)  # 1
    if not verification_code:
        return Response({
                'verified': False,
                'message': 'Please post a valid verification code to verify.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        verification_code_obj = VerificationCode.objects.get(verification_code=verification_code)  # 2
        verified = verification_code_obj.verify()  # 3
        if verified['verified']:
            return Response({
                    'verified': True,
                    'message': verified['message'],
                }, status=HTTP_200_OK
            )
        else:
            return Response({
                    'verified': False,
                    'message': verified['message'],
                }, status=HTTP_400_BAD_REQUEST
            )
    except VerificationCode.DoesNotExist:
        return Response({
                'verified': False,
                'message': 'No verification code found with provided code.'
            }, status=HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_verify_resend(request):
    '''
    --Resend verification email view--
    ==========================================================================================================
    :params: str email (required)
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    1) Checks for required email is in the request. If no email returns 400.
    2) Checks for required password in the request. If no password returns 400.
    2) Checks that user object exists with given email. If no user returns 400.
    4) Calls send_user_verification_email. Returns the appropriate message and 200 
       if verifcation resent else 400.
    ==========================================================================================================
    '''
    email = request.data.get('email', None)  # 1
    if not email:
        return Response({
                'verifification_sent': False,
                'message': 'Please post a valid email address to resend verification email.'
            }, status=HTTP_400_BAD_REQUEST
        )
    
    password = request.data.get('password', None)  # 2
    if not password:
        return Response({
                'verifification_sent': False,
                'message': 'Please post a valid password to resend verification email.'
            }, status=HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)  # 3
        if not user.check_password(password):
            return Response({
                'verifification_sent': False,
                'message': 'Password does not match what we have on file. Please try again.'
            }, status=HTTP_400_BAD_REQUEST)

        verification_code = user.verification_codes.latest('created_at')

        verification_code_sent = verification_code.send_user_verification_email()  # 4

        if verification_code_sent['verification_sent']:
            return Response({
                    'verifification_sent': verification_code_sent['verification_sent'],
                    'message': verification_code_sent['message'],
                }, status=HTTP_200_OK
            )
        else:
            return Response({
                    'verifification_sent': verification_code_sent['verification_sent'],
                    'message': verification_code_sent['message'],
                }, status=HTTP_400_BAD_REQUEST
            )

    except User.DoesNotExist:
        return Response({
                'verifification_sent': False,
                'message': 'No user found with provided email.'
            }, status=HTTP_400_BAD_REQUEST
        )


user_login_refresh = TokenRefreshView().as_view()


class MyObtainTokenPairView(TokenObtainPairView):  # 1
    '''
    --User obtain token view (Login) djangorestframework-simplejwt--
    ==========================================================================================================
    :param: str settings.SIMPLE_JWT_LOGIN_USERNAME_FIELD ('e.g. `email` or `username`') (required)
    :param: str password (required)
    :returns: Response.HTTP_STATUS_CODE. 
    :returns: Token, RefreshToken.
    1) Attmpts to obtain a token pair with email & password. Returns 200 else 400.
    ==========================================================================================================
    '''
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainPairSerializer

user_login = MyObtainTokenPairView().as_view()


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_logout(request):
    '''
    --Logout user view--
    ==========================================================================================================
    :param: str refresh token (required).
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    1) Checks that refresh token in request. If no token returns 400.
    2) Checks that a refresh object exists. If no returns 400.
    3) Attempts to blacklist (logout) the refresh token. Returns 204 else 400.
    ==========================================================================================================
    '''
    token_str = request.data.get('refresh', None)  # 1
    if not token_str:
        return Response({
                'logged_out': False,
                'message': 'Please post a valid refresh token to logout.'
            }, status=HTTP_400_BAD_REQUEST
        )
    
    try:
    
        token = RefreshToken(token_str)  # 2
        try:
            token.blacklist()  # 3
            return Response({
                    'logged_out': True,
                    'message': 'User logged out successfully'
                }, status=HTTP_204_NO_CONTENT
            )
        except:
            return Response({
                    'logged_out': False,
                    'message': 'User is already logged out'
                }, status=HTTP_400_BAD_REQUEST
            )

    except TokenError:
        return Response({
                'logged_out': False,
                'message': 'No token found with given credentials.'
            }, status=HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_password_reset_send(request):
    '''
    --Send password reset link view--
    ==========================================================================================================
    :param: str email (required).
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    1) Checks for email in request. If no returns 400 and messsage.
    2) Checks that user object exists. If no returns 400 and message.
    3) Checks if any PasswordResetCode objects exist for user. If so resends it 
       and returns 200 and message.
    4) Attempts to create a new PasswordResetCode object for the user.
       If success returns 200 and message else 400 and messsage.
    ==========================================================================================================
    '''
    email = request.data.get('email', None)  # 1
    if not email:
        return Response({
                'password_reset_link_sent': False,
                'message': 'Please post a valid email to get reset password link.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)  # 2

        codes_exist = PasswordResetCode.objects.filter(user=user).exists()
        if codes_exist:
            password_reset_link_sent = PasswordResetCode.objects.filter(
                                            user=user).latest('created_at').send_user_password_reset_email()  # 3
            return Response({
                    'password_reset_link_sent': password_reset_link_sent['password_reset_link_sent'],
                    'message': password_reset_link_sent['message']
                }, status=HTTP_200_OK
            )

        code = PasswordResetCode.objects.create(user=user)  # 4
        password_reset_link_sent = code.send_user_password_reset_email()

        return Response({
                'password_reset_link_sent': password_reset_link_sent['password_reset_link_sent'],
                'message': password_reset_link_sent['message']
            }, status=HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response({
                'message': 'No user found with the provided email.'
            }, status=HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes((AllowAny,))
def user_password_reset(request):
    '''
    --Password reset view--
    ==========================================================================================================
    :param: str password_reset_code (required).
    :param: str password (required),
    :param: str password2 (required).
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    1) Checks that password reset code included in request. If no returns 400 and message.
    2) Checks that password and password 2 are included in the request. If no returns 400 and message.
    3) Checks that both new passwords match. If no returns 400 and message.
    4) Attempts to get the password code object. If no returns 400 and message.
    5) Calls verify on the PasswordCode object. Return either True or False and a message.
    ==========================================================================================================
    '''
    password_reset_code = request.data.get('password_reset_code', None)  # 1
    if not password_reset_code:
        return Response({
                'password_reset': False,
                'message': 'Please post a valid password reset code to reset password.'
            }, status=HTTP_400_BAD_REQUEST
        )

    password = request.data.get('password', None)
    password2 = request.data.get('password2', None)  # 2
    if password is None or password2 is None:
        return Response({
                'password_reset': False,
                'message': 'Please post two new matching passwords to reset password.'
            }, status=HTTP_400_BAD_REQUEST
        )

    if password != password2:
        return Response({
                'password_reset': False,
                'message': 'Please post matching passwords to reset password.'  # 3
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        password_reset_code_object = PasswordResetCode.objects.get(password_reset_code=password_reset_code)  # 4
        password_reset = password_reset_code_object.verify(password)  # 5

        if password_reset['password_reset']:
            return Response({
                    'password_reset': True,
                    'message': password_reset['message']
                }, status=HTTP_200_OK
            )
        else:
            return Response({
                    'password_reset': False,
                    'message': password_reset['message']
                }, status=HTTP_400_BAD_REQUEST
            )
    except PasswordResetCode.DoesNotExist:
        return Response({
                'password_reset': False,
                'message': 'No password reset code found with provided code.'
            }, status=HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def user_update(request):
    """
    --Update a User instance--
    ==========================================================================================================
    :param: str partial.
    :returns: str message
    1) Checks for partial keyword in request. This may be needed in the future once we add more fields to user.
    2) Checks for email in request. You can not do that.
    3) Verifies that there is at least one field to be updated included in the request.
    4) Serializes request user.
    5) Attempts to save the user serializer. If errors returns 400 and errors.
    6) Saves serializer instance and returns 200 and user.
    ==========================================================================================================
    """
    partial = request.data.get('partial', False)  # 1

    email = request.data.get('email', None)  # 2
    if email:
        return Response({
                'updated': False,
                'message': 'You cannot update your email.'
            }, status=HTTP_400_BAD_REQUEST
        )

    if not request.data.keys():  # 3
        return Response({
                'updated': False,
                'message': 'You need to include at least one field to update.'
            }, status=HTTP_400_BAD_REQUEST
        )
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=partial)  # 4

    if serializer.is_valid():  # 5
        serializer.save()  # 6
        return Response({
                'updated': True,
                'message': 'User updated successfully.',
                'user': serializer.data
            }, status=HTTP_200_OK
        )
    else:
        return Response({
                'updated': False,
                'message': serializer.errors
            }, status=HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def user_delete(request):
    """
    --Delete a User instance (make inactive)--
    ==========================================================================================================
    1) Checks wether this delete is confirmed. If False returns 400.
    2) Checks to make sure there is a refresh token string in the request.
       If no returns 400.
    3) Attempts to find the RefreshToken associated with this user. If no
       returns 400.
    4) Attempts to blacklist the users refresh token. If no returns 400.
    5) Changes the user is_active to False (delete user). Returns 204.
    ==========================================================================================================
    """
    delete_confirmed = request.data.get('delete_confirmed', False)  # 1
    if not delete_confirmed:
        return Response({
                'deleted': False,
                'message': 'Please confirm that you want to delete user data.'
            }, status=HTTP_400_BAD_REQUEST
        )

    user = request.user
    token_str = request.data.get('refresh', None)  # 2
    if not token_str:
        return Response({
                'deleted': False,
                'message': 'Please post a valid refresh token to delete.'
            }, status=HTTP_400_BAD_REQUEST
        )

    try:
        token = RefreshToken(token_str)  # 3
        try:
            token.blacklist()  # 4
        except:
            return Response({
                    'deleted': False,
                    'message': 'Unable to blacklist token. Please check credentials.'
                }, status=HTTP_400_BAD_REQUEST
            )

    except TokenError:
        return Response({
                'deleted': False,
                'message': 'No token found with given credentials.'
            }, status=HTTP_400_BAD_REQUEST
        )

    user.is_active = False  # 5
    user.save()
    return Response({
            'deleted': True,
            'message': 'User deleted successfully.'
        }, status=HTTP_204_NO_CONTENT
    )


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user(request):
    '''
    --User detail view--
    ==========================================================================================================
    :param: request.user
    :returns: User serialized.
    :returns: Response.HTTP_STATUS_CODE.
    1) Attempts to get the user_pub_id from request. If no sets to None.
    2) If no user_pub_id in request sets request.user as user.
    3) Attempts to get the user with provided user_pub_id. If no returns 400.
    4) Serialize and returns the user.
    ==========================================================================================================
    '''
    user_pub_id = request.data.get('user_pub_id', None)  # 1

    if not user_pub_id:
        user = request.user  # 2
    else:
        try:
            user = User.objects.get(pub_id=user_pub_id)  # 3
        except User.DoesNotExist:
            return Response({
                    'message': 'No user found with provided user id.'
                }, status=HTTP_400_BAD_REQUEST
            )
    serialized_user = UserSerializer(user).data  # 4
    return Response({
                'user': serialized_user 
            }, status=HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def user_follow(request):
    '''
    --User follow unfollow view--
    ==========================================================================================================
    :param: follow_pub_id str (required)
    1) Checks for follow_pub_id in request. If not returns 400 and message.
    2) Attempts to lookup a user with the param follow_pub_id. If no returns 400 and message.
    3) Gets the current user.
    4) Calls follow_user on user model. Returns 200 or 400 and appropriate message.
    :returns: boolean followed.
    :returns: str message.
    :returns: Response.HTTP_STATUS_CODE.
    ==========================================================================================================
    '''
    follow_pub_id = request.data.get('follow_pub_id', None)  # 1
    if not follow_pub_id:
        return Response({
            'followed': False,
            'message': 'Please post a valid id of a user to follow.'
        },status=HTTP_400_BAD_REQUEST)

    try:
        user_to_follow = User.objects.get(pub_id=follow_pub_id)  # 2
    except User.DoesNotExist:
        return Response({
                'followed': False,
                'message': 'No user found with provided pub id.'
            }, status=HTTP_400_BAD_REQUEST)

    user = request.user  # 3

    followed = user.follow_user(follow_pub_id)  # 4

    if followed['followed']:
        return Response({
            'followed': True,
            'message': followed['message']
        }, status=HTTP_201_CREATED
    )
    else:
        return Response({
            'followed': False,
            'message': followed['message']
        }, status=HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_posts(request):
    '''
    --All user posts view--
    ==========================================================================================================
    Returns nested representations of all posts for this user. Paginates the quereyset.
    ==========================================================================================================
    '''
    posts_to_paginate = \
        Post.objects.prefetch_related('bookmarks').select_related('previouspost').select_related('nextpost').filter(author=request.user, is_active=True)
    all_posts = get_paginated_queryset(request, posts_to_paginate, PostSerializer)

    return all_posts


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_following(request):
    '''
    --All user following view--
    ==========================================================================================================
    Returns all users a user is folllowing. Paginates the queryset.
    ==========================================================================================================
    '''
    user_followings = request.user.following.all()

    all_followings = get_paginated_queryset(request, user_followings, UserFollowingSerializer)

    return all_followings


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_followers(request):
    '''
    --All user followers view--
    ==========================================================================================================
    Returns all users that are following him. Paginates the queryset.
    ==========================================================================================================
    '''
    user_followers = request.user.followers.all()

    all_followers = get_paginated_queryset(request, user_followers, UserFollowersSerializer)

    return all_followers


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_following_posts(request):
    '''
    --All user following posts view--
    ==========================================================================================================
    Returns all post by those hes following. Paginates the queryset.
    ==========================================================================================================
    '''
    user_following = request.user.following.all()

    posts = []

    for follow in user_following:
        follow_posts = Post.objects.filter(author=follow.following.id, is_active=True)
        for post in follow_posts:
            posts.append(post)

    all_following_posts = get_paginated_queryset(request, posts, PostSerializer)

    return all_following_posts


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_follower_posts(request):
    '''
    --All user following posts view--
    ==========================================================================================================
    Returns all post by those hes following. Paginates the queryset.
    ==========================================================================================================
    '''
    user_followers = request.user.followers.all()

    posts = []

    for follow in user_followers:
        follow_posts = Post.objects.filter(author=follow.user.id, is_active=True)
        for post in follow_posts:
            posts.append(post)

    all_followers_posts = get_paginated_queryset(request, posts, PostSerializer)

    return all_followers_posts


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_bookmarks(request):
    '''
    --All user bookmarked posts--
    ==========================================================================================================
    Returns all posts a user has bookmarked. Paginates the queryset.
    ==========================================================================================================
    '''
    user_bookmarks = Post.objects.filter(bookmarks=request.user, is_active=True)
    all_user_bookmarks = get_paginated_queryset(request, user_bookmarks, PostSerializer)
    return all_user_bookmarks


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_likes(request):
    '''
    --All posts liked view--
    ==========================================================================================================
    Returns all posts liked by a user. Paginates the queryset.
    ==========================================================================================================
    '''
    user = request.user
    user_liked_posts = Like.objects.filter(users=user)
    liked_posts = []
    for like in user_liked_posts:
        if not like.post.is_active:
            continue
        liked_posts.append(like.post)

    all_liked_posts = get_paginated_queryset(request, liked_posts, PostSerializer)
    return all_liked_posts


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_dislikes(request):
    '''
    --All posts liked view--
    ==========================================================================================================
    Returns all posts liked by a user. Paginates the queryset.
    ==========================================================================================================
    '''
    user = request.user
    user_disliked_posts = DisLike.objects.filter(users=user)
    disliked_posts = []
    for dislike in user_disliked_posts:
        if not dislike.post.is_active:
            continue
        disliked_posts.append(dislike.post)

    all_disliked_posts = get_paginated_queryset(request, disliked_posts, PostSerializer)
    return all_disliked_posts
