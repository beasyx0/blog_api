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
            search_text, config='english'
        )
        search_rank = SearchRank(search_vectors, search_query)
        trigram_similarity = TrigramSimilarity('title', search_text)
        return (
            self.filter(search_vector=search_query)
                # .prefetch_related('tags')
                .prefetch_related('bookmarks')
                .annotate(rank=search_rank + trigram_similarity)
                .order_by('-rank')
        )
    def featured(self):
        return self.filter(featured=True)

    def most_bookmarked(self):
        return self.annotate(num_bookmarks=Count(F('bookmarks'))).order_by('-num_bookmarks')



class PostManager(models.Manager):

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def search(self, search_text):
        return self.get_queryset().search(search_text)

    # def featured(self):
    #     return self.get_queryset().featured()

    # def most_viewed(self):
    #     return self.get_queryset().most_viewed()

    # def most_bookmarked(self):
    #     return self.get_queryset().most_bookmarked()
