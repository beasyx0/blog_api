# Generated by Django 3.1.13 on 2021-07-13 02:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210712_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, null=True)),
                ('updated_at', models.DateTimeField(editable=False, null=True)),
                ('verification_code', models.UUIDField(editable=False, unique=True)),
                ('code_expiration', models.DateTimeField(default=datetime.datetime(2021, 7, 16, 2, 29, 16, 338295, tzinfo=utc))),
                ('user_to_verify', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Verification Code',
                'verbose_name_plural': 'Verification Codes',
            },
        ),
    ]
