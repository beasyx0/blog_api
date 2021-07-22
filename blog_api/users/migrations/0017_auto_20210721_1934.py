# Generated by Django 3.1.13 on 2021-07-21 23:34

import blog_api.users.model_validators
import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20210721_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, validators=[blog_api.users.model_validators.validate_name_no_special_chars]),
        ),
    ]
