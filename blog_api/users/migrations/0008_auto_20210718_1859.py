# Generated by Django 3.1.13 on 2021-07-18 22:59

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210718_0055'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
