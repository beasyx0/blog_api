from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.contrib.postgres.search import SearchVector

from blog_api.posts.models import Post, Like, DisLike


@receiver(post_save, sender=Post)
def update_search_vectors(sender, instance, created, **kwargs):
    search_vectors = SearchVector('title', weight='A') + SearchVector('content', weight='B')
    if created:
        instance.search_vector = search_vectors
        instance.save()


@receiver(post_save, sender=Post)
def create_like_dislike_objects(sender, instance, created, **kwargs):
    if created:
        Like.objects.create(post=instance)
        DisLike.objects.create(post=instance)
