# Generated by Django 4.1.7 on 2023-06-11 19:13

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='YoutubeVideoId',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('video_url', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EnglishComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_id', models.CharField(max_length=255)),
                ('original_text', models.TextField()),
                ('parent_id', models.CharField(default=None, max_length=255)),
                ('author_name', models.CharField(max_length=255)),
                ('channel_id', models.CharField(max_length=255)),
                ('published_at', models.DateTimeField()),
                ('created_at', models.DateField(default=None)),
                ('update_at', models.DateTimeField()),
                ('label', models.CharField(default=None, max_length=255)),
                ('video_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encomment_video', to='youtube_app.youtubevideoid')),
            ],
        ),
        migrations.CreateModel(
            name='EmojiesInComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_id', models.CharField(max_length=255)),
                ('original_text', models.TextField()),
                ('parent_id', models.CharField(default=None, max_length=255)),
                ('author_name', models.CharField(max_length=255)),
                ('channel_id', models.CharField(max_length=255)),
                ('published_at', models.DateTimeField()),
                ('created_at', models.DateField(default=None)),
                ('update_at', models.DateTimeField()),
                ('label', models.CharField(default=None, max_length=255)),
                ('video_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emcomment_video', to='youtube_app.youtubevideoid')),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_id', models.CharField(max_length=255)),
                ('original_text', models.TextField()),
                ('parent_id', models.CharField(default=None, max_length=255)),
                ('author_name', models.CharField(max_length=255)),
                ('channel_id', models.CharField(max_length=255)),
                ('published_at', models.DateTimeField()),
                ('created_at', models.DateField(default=None)),
                ('update_at', models.DateTimeField()),
                ('label', models.CharField(default=None, max_length=255)),
                ('video_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_video', to='youtube_app.youtubevideoid')),
            ],
        ),
        migrations.CreateModel(
            name='CleanedComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_id', models.CharField(max_length=255)),
                ('original_text', models.TextField()),
                ('parent_id', models.CharField(default=None, max_length=255)),
                ('author_name', models.CharField(max_length=255)),
                ('channel_id', models.CharField(max_length=255)),
                ('published_at', models.DateTimeField()),
                ('created_at', models.DateField(default=None)),
                ('update_at', models.DateTimeField()),
                ('cleaned_text', models.TextField()),
                ('cleaned_date', models.DateTimeField(auto_now_add=True)),
                ('video_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ccomment_video', to='youtube_app.youtubevideoid')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
