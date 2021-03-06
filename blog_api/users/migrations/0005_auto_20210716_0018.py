# Generated by Django 3.1.13 on 2021-07-16 00:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210713_0329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='code_expiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 19, 0, 18, 18, 983394, tzinfo=utc)),
        ),
    ]
