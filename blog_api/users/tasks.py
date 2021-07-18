import logging
logger = logging.getLogger(__name__)

from rest_framework_simplejwt.tokens import OutstandingToken

from django.contrib.auth import get_user_model
from django.utils import timezone

from config import celery_app

User = get_user_model()


@celery_app.task()
def flush_outstanding_tokens():
    '''Flushes any expired tokens in the outstanding token list'''
    OutstandingToken.objects.filter(expires_at__lte=timezone.now()).delete()
    logger.info('[Celery] Flushed OutstandingToken objects from database...')
