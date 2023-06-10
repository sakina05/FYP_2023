from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)

class CommentInfo(models.Model):
    video_id = models.CharField(max_length=100)
    url = models.URLField()
    total_comments = models.IntegerField()

    def __str__(self):
        return self.video_id

class Comment(models.Model):
    video_id = models.CharField(max_length=255)
    video_url = models.URLField()
    comment_text = models.TextField()

    def __str__(self):
        return self.comment_text

class CleanedComment(models.Model):
    comment_text = models.TextField()

    def __str__(self):
        return self. comment_text






