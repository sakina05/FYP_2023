import os
from datetime import datetime

import form as form

from .forms import SentimentAnalyzeForm, SpamDetectionForm
import mpld3
import nltk
from matplotlib import pyplot as plt
from wordcloud import WordCloud
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
import os
import googleapiclient.discovery
import googleapiclient.errors
from .models import Comments, YoutubeVideoId, EmojiesInComments, EnglishComment, CleanedComment, EmojiesClean, \
    SpamCleanComment


model_dir = os.path.join(settings.BASE_DIR, 'models')
model_dirs = os.path.join(settings.BASE_DIR, 'spam_model')
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
                        label=comment['label'],
                        spamlabel=comment['spamlabel']
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
    demo_video_id = YoutubeVideoId.objects.all()
    for video_item in demo_video_id:
        print(video_item)
        print(len(Comments.objects.filter(video_id=video_item.video_id)))
        print("-------------------------------\n")
    print(demo_video_id)
    return HttpResponse(f"Recorded Inserted {demo_video_id} Here")

def ploting_accuracy():
    labels = ['Random Forest', 'Decision Tree', 'STOCHASTIC GRADIENT DESCENT', 'Naive Bayes']
    accuracies = [90.7, 86.6, 89, 78]
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'orange']
    fig = plt.figure(figsize=(15, 5))
    plt.bar(labels, accuracies, color=colors)
    plt.title('Classifier Accuracies for Analysis')
    plt.xlabel('Classifier')
    plt.ylabel('Accuracy')
    plt.ylim(0.0, 100.0)  # Set y-axis limit from 0 to 100

    for i, v in enumerate(accuracies):
        plt.text(i, v + 1, str(v), ha='center', va='bottom')

    return mpld3.fig_to_html(fig)


def count_comment_per_video():
    v_count = Comments.objects.values('video_id').annotate(count=Count('video_id'))
    video_counts_list = list(v_count.values_list('count', flat=True))
    video_counts_id = list(v_count.values_list('video_id', flat=True))
    fig, ax = plt.subplots()
    ax.set_title("Comments w.r.t Video")
    ax.pie(video_counts_list, labels=video_counts_id)

    return mpld3.fig_to_html(fig)


def fetch_eng_comments(request, video_id):
    # print(video_id)
    context = {}
    counts_senti = ''
    counts_pie_senti = ''
    fetch_data = EnglishComment.objects.filter(video_id=video_id, label__isnull=False)
    print(fetch_data.count())
    if fetch_data.count() > 0:
        counts_senti = video_sentiment_count(fetch_data)
        counts_pie_senti = video_sentiment_pie(fetch_data)
    context['gr1'] = counts_senti
    context['gr2'] = counts_pie_senti
    return render(request, 'eng_comment.html', context)

def fetch_emoji_comments(request, video_id):
    context = {}
    counts_senti = ''
    counts_pie_senti = ''
    fetch_data = EmojiesClean.objects.filter(video_id=video_id, label__isnull=False)
    if fetch_data.count() > 0:
        counts_senti = video_sentiment_count(fetch_data)
        counts_pie_senti = video_sentiment_pie(fetch_data)
    context['gr1'] = counts_senti
    context['gr2'] = counts_pie_senti
    return render(request, 'emj_comment.html', context)


def video_sentiment_count(vide_data):
    fig = plt.figure(figsize=(8, 5))
    v_count = vide_data.values('label').annotate(count=Count('label'))
    video_counts_list = list(v_count.values_list('count', flat=True))
    video_counts_id = list(v_count.values_list('label', flat=True))
    colors = ['grey', 'red', 'blue', 'green']
    plt.bar(video_counts_id, video_counts_list, color=colors)
    plt.title('Count Sentiment')
    plt.xlabel('Sentiment')
    plt.ylabel('Counts')
    return mpld3.fig_to_html(fig)
#
#
def video_sentiment_pie(vide_data):
    fig = plt.figure(figsize=(8, 5))
    v_count = vide_data.values('label').annotate(count=Count('label'))
    video_counts_list = list(v_count.values_list('count', flat=True))
    video_counts_id = list(v_count.values_list('label', flat=True))
    fig, ax = plt.subplots()
    ax.set_title("Comments w.r.t Sentiments")
    ax.pie(video_counts_list, labels=video_counts_id)
    return mpld3.fig_to_html(fig)

def visualization(request):
    text1 = []
    graph_1 = CleanedComment.objects.all().values_list('original_text', flat=True)
    for text in graph_1:
        text1.append(text.encode('utf-8'))
    wordcloud = WordCloud(width=800, height=400, max_words=100, background_color='white')
    wordcloud.generate(' '.join(text1.decode('utf-8') if isinstance(text1, bytes) else str(text1) for text1 in text1))
    abf = plt.figure(figsize=(8, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    html_fig = mpld3.fig_to_html(abf)
    accuracy_grapg = ploting_accuracy()
    total_video_comment = count_comment_per_video()
    context = {
        'gr1': html_fig,
        'gr2': accuracy_grapg,
        'gr3': total_video_comment,
    }
    return render(request, 'sentvisualization.html', context)

def spamvisualization(request):
    text1 = []
    graph_1 = SpamCleanComment.objects.all().values_list('original_text', flat=True)
    for text in graph_1:
        text1.append(text.encode('utf-8'))
    wordcloud = WordCloud(width=800, height=400, max_words=100, background_color='white')
    wordcloud.generate(' '.join(text1.decode('utf-8') if isinstance(text1, bytes) else str(text1) for text1 in text1))
    abf = plt.figure(figsize=(8, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    html_fig = mpld3.fig_to_html(abf)
    accuracy_grapg = spamploting_accuracy()
    # total_video_comment = count_comment_per_video()
    context = {
        'gr1': html_fig,
        'gr2': accuracy_grapg,
        # 'gr3': total_video_comment,
    }
    return render(request, 'spamvisualization.html', context)

def spamploting_accuracy():
    labels = ['LOGISTIC REGRESSION', 'SVM','GRADIENT BOOSTING']
    accuracies = [95, 84.6, 97]
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'orange']
    fig = plt.figure(figsize=(8, 5))
    plt.bar(labels, accuracies, color=colors)
    plt.title('Classifier Accuracies for Analysis')
    plt.xlabel('Classifier')
    plt.ylabel('Accuracy')
    plt.ylim(0.0, 100.0)  # Set y-axis limit from 0 to 100

    for i, v in enumerate(accuracies):
        plt.text(i, v + 1, str(v), ha='center', va='bottom')

    return mpld3.fig_to_html(fig)

import joblib
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder

from django.shortcuts import render
from .forms import SentimentAnalyzeForm

# nltk.download('punkt')
# nltk.download('stopwords')

sentiment_model = joblib.load(os.path.join(model_dir, 'eng_decision_tree.h5'))
spam_model = joblib.load(os.path.join(model_dirs, 'spam_svm_model.h5'))

# Load the fitted vectorizers
sentiment_vectorizer = joblib.load(os.path.join(model_dir, 'vectorizer.pkl'))
spam_vectorizer = joblib.load(os.path.join(model_dirs, 'spam_vectorizer.pkl'))

# Load the label encoders
sentiment_encoder = LabelEncoder()
sentiment_encoder.classes_ = joblib.load(os.path.join(model_dir, 'encoder.pkl'))

spam_encoder = LabelEncoder()
spam_encoder.classes_ = joblib.load(os.path.join(model_dirs, 'spam_encoder.pkl'))

def preprocess_comment(comment):
    cleaned_comment = re.sub(r'http\S+', '', comment)
    cleaned_comment = word_tokenize(cleaned_comment.lower())
    stop_words = set(stopwords.words('english'))
    cleaned_comment = [word for word in cleaned_comment if word not in stop_words]
    cleaned_comment = ' '.join(cleaned_comment)
    cleaned_comment = re.sub(r'[@%?&!#$^*::/\|=-><.]', '', cleaned_comment)
    return cleaned_comment

def preprocess_spam_comment(comment):
    cleaned_comment = re.sub(r'http\S+', '', comment)
    cleaned_comment = word_tokenize(cleaned_comment.lower())
    stop_words = set(stopwords.words('english'))
    cleaned_comment = [word for word in cleaned_comment if word not in stop_words]
    cleaned_comment = ' '.join(cleaned_comment)
    cleaned_comment = re.sub(r'[@%?&!#$^*::/\|=-><.]', '', cleaned_comment)
    return cleaned_comment

def sentiment_analysis(request):
    if request.method == 'POST':
        form = SentimentAnalyzeForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['input_text']
            print(input_text)
            cleaned_text = preprocess_comment(input_text)

            # Apply the same preprocessing steps as in training
            X_pred_encoded = sentiment_vectorizer.transform([cleaned_text])

            # Make predictions using the trained model
            predictions = sentiment_model.predict(X_pred_encoded)

            # Map predicted labels to sentiments
            sentiment_mapping = {
                1: 'Negative',
                2: 'Neutral',
                3: 'Positive'
            }
            predicted_sentiments = [sentiment_mapping.get(label, 'Unknown') for label in predictions]
            print(predicted_sentiments)
            return render(request, 'sentiment-analysis.html', {'form': form, 'predicted_sentiments': predicted_sentiments})
    else:
        form = SentimentAnalyzeForm()

    return render(request, 'sentiment-analysis.html', {'form': form, 'predicted_sentiments': None})

def spam_detection(request):
    # predicted_labels = None

    if request.method == 'POST':
        spam_form = SpamDetectionForm(request.POST)
        if spam_form.is_valid():
            input_text = spam_form.cleaned_data['input_text']
    # if request.method == 'POST':
    #     spam_form = SpamDetectionForm(request.POST)
    #     if spam_form.is_valid():
    #         input_text = spam_form.cleaned_data['input_text']
            print(input_text)
            cleaned_text = preprocess_spam_comment(input_text)

            # Apply the same preprocessing steps as in training
            X_pred_encoded = spam_vectorizer.transform([cleaned_text])

            # Make predictions using the spam detection model
            predictions = spam_model.predict(X_pred_encoded)

            # Decode the predicted labels using the label encoder
            # predicted_labels = spam_encoder.inverse_transform(predictions)
            predicted_labels = ['Ham' if label == 0 else 'Spam' for label in predictions]

            print(predicted_labels)
            return render(request, 'spam-detection.html', {'spam_form': spam_form, 'predicted_labels': predicted_labels})
    else:
        spam_form = SpamDetectionForm()

        return render(request, 'spam-detection.html', {'spam_form': spam_form, 'predicted_labels': None})