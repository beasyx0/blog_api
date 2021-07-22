# Generated by Django 3.1.13 on 2021-07-21 23:01

import blog_api.users.model_validators
import datetime
import django.contrib.auth.validators
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20210720_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator, blog_api.users.model_validators.validate_username_min_3_letters]),
        ),
    ]