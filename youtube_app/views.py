
from datetime import datetime
import nltk
nltk.download('vader_lexicon')

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .fetch_comments import get_video_comments
from .forms import BasicRegForm, LoginForm, YoutubeUrlForm

import googleapiclient.discovery
import googleapiclient.errors
from .models import Comments, YoutubeVideoId

def homepage(request):
    return render(request, "homepage.html")


def cfetch(request):
    return render(request, "comment-fetching.html")


def sanalysis(request):
    return render(request, "sentiment-analysis.html")


def sdetection(request):
    return render(request, "spam-detection.html")


def aboutus(request):
    return render(request, "about.html")


def models(request):
    return render(request, "models.html")


#
# def signup(request):
#     return render(request, "signup.html")


from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

def index(request):
    context = {}
    login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            user = EmailBackend.authenticate(request, username=username, password=password)
            if user is not None:
                print("Login success")
                login(request, user)
                return HttpResponseRedirect(reverse('homepage'))
            # reverse("news-year-archive", args=(year,)
            else:
                context['login_form_error'] = 'True'
                messages.error(request, 'Login credential not matched, please try valid credential.')
        else:
            context['login_form_error'] = 'True'
            messages.error(request, "ERROR! while saving info please try again")
    else:
        context['login_form_error'] = 'True'
    context['login_form'] = login_form
    # context['current_page'] = 'login'
    return render(request, 'login.html', context)


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


def signup(request):
    context = {}
    reg_form = BasicRegForm()
    if request.method == 'POST':
        reg_form = BasicRegForm(request.POST)
        if reg_form.is_valid():
            reg = reg_form.save(commit=False)
            # reg.is_active = False
            password = reg.password
            reg.set_password(password)
            reg.save()
            messages.info(request, 'Please confirm your email address to complete the registration')
            return HttpResponseRedirect('/')
        else:
            context['teacher_form_error'] = 'True'
            messages.error(request, "ERROR! while saving info please try again")
    context['reg_form'] = reg_form
    context['current_page'] = 'signup'
    return render(request, 'signup.html', context)

def logout_page(request):
    logout(request)
    return redirect('index')



def insert_url(request):
    context = {}
    yt_form = YoutubeUrlForm()
    if request.method == 'POST':
        yt_form = YoutubeUrlForm(request.POST)
        if yt_form.is_valid():
            video_id = yt_form.cleaned_data.get('video_id')
            video_id_parts = video_id.split('=')  # Split the video_id by '='
            if len(video_id_parts) > 1:
                video_id = video_id_parts[1]
                video_id_parts_ampersand = video_id.split('&')  # Split the video_id by '&'
                if len(video_id_parts_ampersand) > 0:
                    video_id = video_id_parts_ampersand[0]
                    YoutubeVideoId.objects.create(
                        id=video_id,
                        video_url=yt_form.cleaned_data.get('video_id')
                    )
                    messages.info(request, 'Please confirm your email address to complete the registration')
                    return HttpResponseRedirect(reverse('fetch-comm'))
                else:
                    messages.error(request, "ERROR! while saving info. Please try again.")
            else:
                messages.error(request, "ERROR! Invalid video URL. Please try again.")
        else:
            messages.error(request, "ERROR! Invalid form. Please try again.")
    context['yt_form'] = yt_form
    context['videos'] = YoutubeVideoId.objects.all()
    return render(request, 'comment-fetching.html', context)


def fetch_comments(request):
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    youtube = googleapiclient.discovery.build(
        settings.API_SERVICE_NAME,
        settings.API_VERSION,
        developerKey=settings.DEVELOPER_KEY
    )

    videos = YoutubeVideoId.objects.all()
    for video_item in videos:
        video_id_parts = video_item.video_url.split('=')  # Split the video_url by '='
        if len(video_id_parts) > 1:
            video_id = video_id_parts[1]
            video_id_parts_ampersand = video_id.split('&')  # Split the video_id by '&'
            if len(video_id_parts_ampersand) > 0:
                video_id = video_id_parts_ampersand[0]

                comments = get_video_comments(youtube, part='snippet, replies', videoId=video_id,
                                              textFormat='plainText')

                # Print the comments
                for comment in comments:
                    Comments.objects.create(
                        comment_id=comment['comment_id'],
                        video_id=comment['video_id'],
                        original_text=comment['text_original'],
                        parent_id=comment['parent_id'],
                        author_name=comment['author_name'],
                        channel_id=comment['author_cid'],
                        published_at=comment['published_at'],
                        created_at=datetime.today(),
                        update_at=comment['updated_at'],
                        label=comment['label']
                    )

                # Update the comment count for the video
                video_item.comment_count = len(comments)
                video_item.save()

    context = {
        'videos': videos
    }
    return render(request, 'comment-fetching.html', context)


from django.db.models import Count


def abc(request):
    videos = YoutubeVideoId.objects.all().annotate(comment_count=Count('comments'))

    for video in videos:
        print(video.video_id)
        comments_count = len(Comments.objects.filter(video_id=video.video_id))
        video.comment_count = comments_count
        video.save()
        print(comments_count)
        print("-------------------------------\n")

    return HttpResponse("Comments count updated successfully")

