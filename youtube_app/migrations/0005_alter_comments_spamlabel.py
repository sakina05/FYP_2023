# Generated by Django 4.2 on 2023-06-25 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_app', '0004_spamcleancomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='spamlabel',
            field=models.CharField(default=None, max_length=255),
        ),
    ]