import uuid
from datetime import timedelta

from django.conf import settings
from django.db.models import Manager, Model, DateTimeField, TextField, CharField, EmailField, IntegerField, \
                                        BooleanField,  ForeignKey, ManyToManyField, SlugField, CASCADE, SET_NULL
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth import get_user_model
User = get_user_model()

from blog_api.posts.managers import PostManager


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


class Post(BaseModel):
    '''
    Blog Post Model.
    '''
    slug = SlugField(editable=False, max_length=255, unique=True)
    title = CharField(max_length=255, blank=False, null=False)
    author = ForeignKey(User, on_delete=SET_NULL, null=True)
    featured = BooleanField(default=False)
    estimated_reading_time = IntegerField(default=0)
    content = TextField(blank=False, null=False)
    bookmarks = ManyToManyField(User, related_name='bookmarked_posts', blank=True)
    previouspost = ForeignKey('self', related_name='previous_post', on_delete=SET_NULL, blank=True, null=True)
    nextpost = ForeignKey('self', related_name='next_post', on_delete=SET_NULL, blank=True, null=True)
    search_vector = SearchVectorField(editable=False, null=True)

    objects = Manager()
    items = PostManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Posts'
        indexes = [GinIndex(fields=['search_vector'])]

    def __str__(self):
        return self.title

    def _get_estimated_reading_time(self):
        content_string = self.content.strip()
        word_count = 1
        for char in content_string:
            if char == " ":
                word_count += 1
        word_count = (word_count / 300)
        if not word_count > 1:
            return 1
        return word_count

    def _get_unique_slug(self):
        slug = slugify(self.title)
        uid = uuid.uuid4().hex
        unique_slug = f'{slug}-{uid}'
        qs_exists = Post.objects.filter(slug=unique_slug)
        if qs_exists:
            _get_unique_slug(self)
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self._get_unique_slug()
        self.estimated_reading_time = self._get_estimated_reading_time()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
