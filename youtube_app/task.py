import os.path
import demoji
import joblib
from celery import shared_task
from datetime import datetime
import pandas as pd
from django.conf import settings
from django.utils import timezone
from youtube_app.fetch_comments import *
from youtube_app.models import *
from googleapiclient.discovery import build
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import model_selection
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

model_dir = os.path.join(settings.BASE_DIR, 'models')


@shared_task
def task_one():
    print("\n\n\n\n\n\n\n\n#######################################\n")
    print(datetime.now())
    print("\n#######################################\n\n\n\n\n\n\n\n")


@shared_task
def fetch_comments():
    print("\n\n\n\n\n\n\n\n#######################################\n")
    print("Starting")
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    youtube = build(
        settings.API_SERVICE_NAME,
        settings.API_VERSION,
        developerKey=settings.DEVELOPER_KEY,
        cache_discovery=False
    )

    print("\n\n\n\n\n\n\n\n#######################################\n", YoutubeVideoId.objects.all())
    for video_item in YoutubeVideoId.objects.all():

        print("Starting: ", video_item.id)
        comments = get_video_comments(youtube, part='snippet, replies', videoId=video_item.id,
                                      textFormat='plainText')

        print(f"Length: {len(comments)}")
        latest_published_at = Comments.objects.filter(video_id=video_item.id)

        if latest_published_at:
            latest_published_at = latest_published_at.latest('published_at').published_at
            latest_published_at = latest_published_at.astimezone(timezone.utc).replace(tzinfo=None)
            # print(f"Lastest Publish date :{latest_published_at}")

            # Print the comments
            for comment in comments:
                # print(comment)
                comment_published_at = datetime.strptime(comment['published_at'], '%Y-%m-%dT%H:%M:%SZ')
                if latest_published_at < comment_published_at:
                    insert_comments_into_database(comment)
        else:
            for comment in comments:
                # print(comment)
                insert_comments_into_database(comment)


@shared_task
def comment_labeling():
    print("length of comment", len(CleanedComment.objects.all()))
    # for comment in CleanedComment.objects.filter(label=''):
    #     print(comment.original_text)
    #     if len(comment.original_text) > 10:
    #         lan_code = detect_lang(comment.original_text)
    #         if lan_code == 'en':
    #             comment.label = sentiment_analyzers(comment.original_text)
    #             comment.save()
    for comment1 in CleanedComment.objects.filter(label=''):
        comment1.label = sentiment_analyzers(comment1.original_text)
        comment1.save()
    print("Comments labeling done")

@shared_task
def ecomment_labeling():
    print("length of comment", len(CleanedComment.objects.all()))
    # for comment in CleanedComment.objects.filter(label=''):
    #     print(comment.original_text)
    #     if len(comment.original_text) > 10:
    #         lan_code = detect_lang(comment.original_text)
    #         if lan_code == 'en':
    #             comment.label = sentiment_analyzers(comment.original_text)
    #             comment.save()
    for comment1 in EmojiesClean.objects.filter(label=''):
        comment1.label = sentiment_analyzers(comment1.original_text)
        comment1.save()
    print("Emojies labeling done")


@shared_task
def clean_comment():
    print("Inside task clean data or data preprocessing")
    CleanedComment.objects.all().delete()
    for comment in Comments.objects.all():
        try:
            clean_text, clean_emoji = comment_cleaning(comment.original_text)
            print(clean_text)
            CleanedComment.objects.create(
                comment_id=comment.comment_id,
                video_id=YoutubeVideoId.objects.get(id=comment.video_id),
                original_text=clean_text,
                parent_id=comment.parent_id,
                author_name=comment.author_name,
                channel_id=comment.channel_id,
                published_at=comment.published_at,
                created_at=comment.created_at,
                update_at=comment.update_at,
                label=comment.label
            )
        except Exception as e:
            print(f"Cleaning comment failed: {e}")




@shared_task
def english_model():
    queryset = EnglishComment.objects.all()
    data = list(queryset.values())
    df = pd.DataFrame(data)
    df = df.dropna()
    print(type(df))
    print(df.columns)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['original_text'])
    encoder = LabelEncoder()
    y = encoder.fit_transform(df['label'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    dt_model = DecisionTreeClassifier()
    dt_model.fit(X_train, y_train)
    y_pred = dt_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    joblib.dump(dt_model, os.path.join(model_dir, 'eng_decision_tree.h5'))
    print("English Accuracy:", accuracy)


@shared_task()
def e_model():
    queryset = EmojiesClean.objects.filter(label__isnull=False, original_text__isnull=False)
    data = list(queryset.values())
    df = pd.DataFrame(data)

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['original_text'])
    encoder = LabelEncoder()
    y = encoder.fit_transform(df['label'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the Decision Tree Classifier
    dt_model = DecisionTreeClassifier()
    dt_model.fit(X_train, y_train)
    y_pred = dt_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    joblib.dump(dt_model, os.path.join(model_dir, 'emoji_decision_tree.h5'))
    print("Emoji Accuracy:", accuracy)


def insert_comments_into_database(comment):
    Comments.objects.create(
        comment_id=comment['comment_id'],
        video_id=YoutubeVideoId.objects.get(id=comment['video_id']),
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


@shared_task()
def emoji_extraction():
    for comment in Comments.objects.all():
        emoji_list = find_emoji_text(comment.original_text)
        if emoji_list:
            EmojiesInComments.objects.create(
                comment_id=comment.comment_id,
                video_id=YoutubeVideoId.objects.get(id=comment.video_id),
                original_text=' '.join(emoji_list),
                parent_id=comment.parent_id,
                author_name=comment.author_name,
                channel_id=comment.channel_id,
                published_at=comment.published_at,
                created_at=comment.created_at,
                update_at=comment.update_at,
                label=comment.label
            )


@shared_task()
def demoji_the_emoji():
    EmojiesClean.objects.all().delete()
    for comment in EmojiesInComments.objects.all():
        text_emoji = demoji.findall(comment.original_text)
        EmojiesClean.objects.create(
            comment_id=comment.comment_id,
            video_id=YoutubeVideoId.objects.get(id=comment.video_id),
            original_text=list(text_emoji.values()),
            parent_id=comment.parent_id,
            author_name=comment.author_name,
            channel_id=comment.channel_id,
            published_at=comment.published_at,
            created_at=comment.created_at,
            update_at=comment.update_at,
            label=comment.label
        )
@shared_task
def spamclean_comment():
    print("Inside task clean data or data preprocessing")
    SpamCleanComment.objects.all().delete()
    for comment in Comments.objects.all():
        try:
            start_cleaning = spamcomment_cleaning(comment.original_text)
            print(start_cleaning)
            SpamCleanComment.objects.create(
                comment_id=comment.comment_id,
                video_id=YoutubeVideoId.objects.get(id=comment.video_id),
                original_text=start_cleaning,
                parent_id=comment.parent_id,
                author_name=comment.author_name,
                channel_id=comment.channel_id,
                published_at=comment.published_at,
                created_at=comment.created_at,
                update_at=comment.update_at,
                label=comment.label,
                spamlabel=comment.spamlabel
            )
        except Exception as e:
            print(f"Spam Cleaning comment failed: {e}")