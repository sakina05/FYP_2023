# Generated by Django 4.2 on 2023-06-25 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_app', '0005_alter_comments_spamlabel'),
    ]

    operations = [
        migrations.AddField(
            model_name='spamcleancomment',
            name='label',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
