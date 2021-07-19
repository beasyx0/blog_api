from django.db.models import signals
from django.dispatch import Signal
from django.db import transaction
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

from blog_api.users.models import User, VerificationCode, PasswordResetCode


@receiver(signals.post_save, sender=User)
def send_user_verification_email_signal(sender, instance, created, **kwargs):
    '''Send user a verification email on first save.'''
    if created:
        code = VerificationCode.objects.create(user_to_verify=instance)
        transaction.on_commit(
            lambda: code.send_user_verification_email()
        )


new_registration = Signal(providing_args=["ip_address", "user_username"])

@receiver(new_registration)
def record_ip_on_new_registration(sender, task_id, **kwargs):
    username = kwargs['user_username']
    ip_address = kwargs['ip_address']
    user = get_object_or_404(User, username=username)
    user.ip_address = ip_address
    user.save()
