# Generated by Django 3.1.13 on 2021-07-28 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_dislike_like'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dislike',
            options={'ordering': ['-created_at'], 'verbose_name_plural': 'Dislikes'},
        ),
        migrations.AddField(
            model_name='post',
            name='dislikes_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='post',
            name='likes_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='post',
            name='score',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
