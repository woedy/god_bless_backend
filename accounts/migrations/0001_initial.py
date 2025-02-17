# Generated by Django 5.1.2 on 2024-11-06 05:25

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('fcm_token', models.TextField(blank=True, null=True)),
                ('otp_code', models.CharField(blank=True, max_length=10, null=True)),
                ('email_token', models.CharField(blank=True, max_length=10, null=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('photo', models.ImageField(blank=True, default=accounts.models.get_default_profile_image, null=True, upload_to=accounts.models.upload_image_path)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('language', models.CharField(blank=True, default='English', max_length=255, null=True)),
                ('location_name', models.CharField(blank=True, max_length=200, null=True)),
                ('lat', models.DecimalField(blank=True, decimal_places=15, max_digits=30, null=True)),
                ('lng', models.DecimalField(blank=True, decimal_places=15, max_digits=30, null=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
