from urllib.parse import urlparse
from .models import Comment

import comments as comments
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.shortcuts import render

from .forms import BasicRegForm, LoginForm
from .models import CommentInfo

import csv
from django.http import HttpResponse
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


def index(request):
    context = {}
    login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            print(username)
            user = EmailBackend.authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                print("Login success")
                return HttpResponseRedirect('/homepage/')
            else:
                context['login_form_error'] = 'True'
                messages.error(request, 'Login credential not matched, please try valid credential.')
        else:
            context['login_form_error'] = 'True'
            messages.error(request, "ERROR! while saving info please try again")
    else:
        context['login_form_error'] = 'True'
    context['login_form'] = login_form
    context['current_page'] = 'login'
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
            return HttpResponseRedirect('/index/')
        else:
            context['teacher_form_error'] = 'True'
            messages.error(request, "ERROR! while saving info please try again")
    context['reg_form'] = reg_form
    context['current_page'] = 'signup'
    return render(request, 'signup.html', context)

import csv

from django.http import HttpResponse
from django.shortcuts import render
from .forms import YouTubeForm
from .models import CommentInfo
from .youtube_api import get_video_comments
from urllib.parse import urlparse, parse_qs
from django.contrib import messages

def fetch_comments(request):
    context = {}
    form = YouTubeForm()

    if request.method == 'POST':
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']

            # Extract video ID from the URL
            parsed_url = urlparse(url)
            if parsed_url.netloc == 'youtu.be':
                video_id = parsed_url.path[1:]
            elif parsed_url.netloc == 'www.youtube.com':
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get('v', [''])[0]
            else:
                messages.error(request, "Invalid YouTube URL")
                return render(request, 'comment-fetching.html', context)

            # Fetch comments using YouTube Data API or any other method
            comments = get_video_comments(url)

            # Save the fetched comments to the database
            for comment_text in comments:
                comment = Comment(video_url=url, comment_text=comment_text)
                comment.save()

            # Save comment info to the database
            total_comments = len(comments)
            comment_info = CommentInfo(video_id=video_id, url=url, total_comments=total_comments)
            comment_info.save()

            # Get the top 5 comments
            top_comments = Comment.objects.filter(video_url=url)[:5]

            # Render the comments in a table
            context['top_comments'] = top_comments

            message_1 = "Comment fetching is successful."
            context['message'] = message_1
        else:
            messages.error(request, "ERROR! while saving info please try again")

    context['form'] = form
    context['comments'] = CommentInfo.objects.all()

    return render(request, 'comment-fetching.html', context)

import csv
import os
from django.http import HttpResponse

def save_csv(request):
    comments = Comment.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Video URL', 'Comment'])

    for comment in comments:
        writer.writerow([comment.video_url, comment.comment_text])

    return response

from django.shortcuts import render
from .models import Comment, CleanedComment
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re


from django.http import JsonResponse
from django.shortcuts import render
from .models import CommentInfo, CleanedComment
from .forms import YouTubeForm

def clean_text(comments):
    cleaned_comments = []
    for comment in comments:
        # Remove URLs from the comment
        comment_text = re.sub(r'http\S+|www\S+', '', comment.comment_text)

        # Tokenize the comment text
        tokens = word_tokenize(comment_text)

        # Remove stopwords from the tokens
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token.lower() not in stop_words]

        # Lemmatize the filtered tokens
        lemmatizer = WordNetLemmatizer()
        cleaned_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

        # Remove special characters from the cleaned tokens
        cleaned_tokens = [re.sub(r'[^a-zA-Z0-9]', '', token) for token in cleaned_tokens if token]

        # Join the cleaned tokens back into a text string
        cleaned_comment_text = ' '.join(cleaned_tokens)

        cleaned_comments.append(cleaned_comment_text)

    return cleaned_comments


from django.shortcuts import render
from .models import Comment
# from .clean_comments import clean_text

from django.shortcuts import render
from .models import Comment
# from .clean_comments import clean_text

def clean_comments(request):
    if request.method == 'POST':
        # Clean the comments
        comments = Comment.objects.all()
        cleaned_comments = clean_text(comments)

        # Save cleaned comments to CleanedComment database
        cleaned_comment_objs = []
        for cleaned_comment in cleaned_comments:
            cleaned_comment_objs.append(CleanedComment(comment_text=cleaned_comment))
        CleanedComment.objects.bulk_create(cleaned_comment_objs)

        # Render the template with the appropriate message
        message_2 = "Your dataset is cleaned."
        return render(request, 'comment-fetching.html', {'message': message_2})

    return render(request, 'comment-fetching.html')




