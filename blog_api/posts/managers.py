from django.db import models
from django.db.models import Count, F
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchVector, TrigramSimilarity,
)


class PostQuerySet(models.QuerySet):

    def search(self, search_text):
        search_vectors = (
            SearchVector(
                'title', weight='A', config='english'
            ) +
            SearchVector(
                StringAgg(
                    'content', delimiter=' '
                ), weight='B', config='english',
            )
        )
        search_query = SearchQuery(
            search_text, config='english',

        )
        search_rank = SearchRank(search_vectors, search_query)
        trigram_similarity = TrigramSimilarity('title', search_text)
        return (
            self.filter(search_vector=search_query, is_active=True)
                .select_related('author')
                .select_related('previouspost')
                .select_related('nextpost')
                .annotate(rank=search_rank + trigram_similarity)
                .order_by('-rank')
        )
    def featured(self):
        return (
            self.prefetch_related('bookmarks')
                .prefetch_related('tags')
                .select_related('author')
                .select_related('previouspost')
                .select_related('nextpost')
                .filter(is_active=True, featured=True)
        )

    def most_liked(self):
        return (
            self.prefetch_related('bookmarks')
                .prefetch_related('tags')
                .select_related('author')
                .select_related('previouspost')
                .select_related('nextpost')
                .filter(is_active=True)
                .order_by('-score')
        )

    def most_disliked(self):
        return (
            self.prefetch_related('bookmarks')
                .prefetch_related('tags')
                .select_related('author')
                .select_related('previouspost')
                .select_related('nextpost')
                .filter(is_active=True)
                .order_by('score')
        )

    def oldest_posts(self):
        return (
            self.prefetch_related('bookmarks')
                .prefetch_related('tags')
                .select_related('author')
                .select_related('previouspost')
                .select_related('nextpost')
                .filter(is_active=True).order_by('created_at')
        )

    def most_bookmarked(self):
        return (
            self.prefetch_related('bookmarks')
                .prefetch_related('tags')
                .select_related('author')
                .select_related('previouspost').select_related('nextpost')
                .filter(is_active=True)
                .annotate(bookmark_count=Count(F('bookmarks')))
                .order_by('-bookmark_count')
        )

class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def search(self, search_text):
        return self.get_queryset().search(search_text)

    def featured(self):
        return self.get_queryset().featured()

    def most_liked(self):
        return self.get_queryset().most_liked()

    def most_disliked(self):
        return self.get_queryset().most_disliked()

    def oldest_posts(self):
        return self.get_queryset().oldest_posts()

    def most_bookmarked(self):
        return self.get_queryset().most_bookmarked()


class TagQuerySet(models.QuerySet):

    def highest_post_count(self):
        return self.annotate(posts_total=Count(F('posts'))).order_by('-posts_total')


class TagManager(models.Manager):

    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def create_or_new(self, name):
        name = name.strip()
        qs = self.get_queryset().filter(name__iexact=name)
        if qs.exists():
            return qs.first(), False
        return self.get_queryset().create(name=name), True

    def comma_to_qs(self, tag_str):
        final_ids = []
        for tag in tag_str.split(','):
            obj, created = self.create_or_new(tag)
            final_ids.append(obj.id)
        qs = self.get_queryset().filter(id__in=final_ids).distinct()
        return qs

    def highest_post_count(self):
        return self.get_queryset().highest_post_count()
