from django.db.models import signals
from django.db import transaction
from django.dispatch import receiver

from blog_api.users.models import User, VerificationCode, PasswordResetCode


@receiver(signals.post_save, sender=User)
def send_user_verification_email_signal(sender, instance, created, **kwargs):
    '''Send user a verification email on first save.'''
    if created:
        code = VerificationCode.objects.create(user_to_verify=instance)
        transaction.on_commit(
            lambda: code.send_user_verification_email()
        )


# @receiver(signals.post_save, sender=PasswordResetCode)
# def send_user_password_reset_email_signal(sender, instance, created, **kwargs):
#     '''Send user password reset link'''
#     if created:
#         transaction.on_commit(
#             lambda: instance.send_user_password_reset_email()
#         )
