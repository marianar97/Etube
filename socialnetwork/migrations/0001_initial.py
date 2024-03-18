# Generated by Django 5.0.2 on 2024-03-18 12:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('thumbnail', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='video',
            fields=[
                ('id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('total_mins', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('thumbnail', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('total_mins', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=200)),
                ('thumbnail', models.CharField(max_length=300)),
                ('ChannelId', models.CharField(max_length=70)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.FileField(blank=True, upload_to='')),
                ('content_type', models.CharField(blank=True, max_length=50)),
                ('following', models.ManyToManyField(related_name='followers', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
