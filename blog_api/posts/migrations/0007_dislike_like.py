# Generated by Django 3.1.13 on 2021-07-28 01:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_auto_20210724_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, null=True)),
                ('updated_at', models.DateTimeField(editable=False, null=True)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='posts.post')),
                ('users', models.ManyToManyField(related_name='post_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DisLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, null=True)),
                ('updated_at', models.DateTimeField(editable=False, null=True)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dislikes', to='posts.post')),
                ('users', models.ManyToManyField(related_name='post_dislikes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
