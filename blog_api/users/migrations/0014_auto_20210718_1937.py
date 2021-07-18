# Generated by Django 3.1.13 on 2021-07-18 19:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20210718_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresetcode',
            name='code_expiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 21, 19, 37, 11, 448896, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='code_expiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 21, 19, 37, 11, 448122, tzinfo=utc)),
        ),
    ]