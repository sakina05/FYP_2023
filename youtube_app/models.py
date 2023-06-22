from django.contrib.auth.models import AbstractUser
from django.db import models
import re

class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)


class YoutubeVideoId(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    video_url = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.id}'


class Comments(models.Model):
    comment_id = models.CharField(max_length=255)
    video_id = models.ForeignKey(YoutubeVideoId, related_name='comment_video', on_delete=models.CASCADE)
    original_text = models.TextField()
    parent_id = models.CharField(max_length=255, default=None)
    author_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    created_at = models.DateField(default=None)
    update_at = models.DateTimeField()
    label = models.CharField(max_length=255, default=None)

    def __str__(self):
        return f'{self.video_id} - {self.author_name} - {self.channel_id}'


# model for EnglishComments
class EnglishComment(models.Model):
    comment_id = models.CharField(max_length=255)
    video_id = models.ForeignKey(YoutubeVideoId, related_name='encomment_video', on_delete=models.CASCADE)
    original_text = models.TextField()
    parent_id = models.CharField(max_length=255, default=None)
    author_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    created_at = models.DateField(default=None)
    update_at = models.DateTimeField()
    label = models.CharField(max_length=255, default=None)

    def __str__(self):
        return f'{self.video_id} - {self.author_name} - {self.channel_id}'


# model for UrduComments
class UrduComment(models.Model):
    comment_id = models.CharField(max_length=255)
    video_id = models.ForeignKey(YoutubeVideoId, related_name='urcomment_video', on_delete=models.CASCADE)
    original_text = models.TextField()
    parent_id = models.CharField(max_length=255, default=None)
    author_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    created_at = models.DateField(default=None)
    update_at = models.DateTimeField()
    label = models.CharField(max_length=255, default=None)

    def __str__(self):
        return f'{self.video_id} - {self.author_name} - {self.channel_id}'


# model for Emojies
class EmojiesInComments(models.Model):
    comment_id = models.CharField(max_length=255)
    video_id = models.ForeignKey(YoutubeVideoId, related_name='emcomment_video', on_delete=models.CASCADE)
    original_text = models.TextField()
    parent_id = models.CharField(max_length=255, default=None)
    author_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    created_at = models.DateField(default=None)
    update_at = models.DateTimeField()
    label = models.CharField(max_length=255, default=None)

    def __str__(self):
        return f'{self.video_id} - {self.author_name} - {self.channel_id}'


class EmojiesClean(models.Model):
    comment_id = models.CharField(max_length=255)
    video_id = models.ForeignKey(YoutubeVideoId, related_name='eccomment_video', on_delete=models.CASCADE)
    original_text = models.TextField()
    parent_id = models.CharField(max_length=255, default=None)
    author_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    created_at = models.DateField(default=None)
    update_at = models.DateTimeField()
    label = models.CharField(max_length=255, default=None)

    def __str__(self):
        return f'{self.video_id} - {self.author_name} - {self.channel_id}'



class CleanedComment(models.Model):
    comment_id = models.CharField(max_length=255)
    video_id = models.ForeignKey(YoutubeVideoId, related_name='ccomment_video', on_delete=models.CASCADE)
    original_text = models.TextField()
    parent_id = models.CharField(max_length=255, default=None)
    author_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    created_at = models.DateField(default=None)
    update_at = models.DateTimeField()
    cleaned_date = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=255, default=None)
    # Add any other fields you need

    def __str__(self):
        return f'{self.video_id} - {self.author_name} - {self.channel_id}'