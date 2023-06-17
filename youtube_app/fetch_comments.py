
from .models import EnglishComment
import re
import nltk
import emoji
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect, LangDetectException
sentiments = SentimentIntensityAnalyzer()

def get_video_comments(youtube, **kwargs):
    comments = []
    results = youtube.commentThreads().list(**kwargs).execute()

    while results:
        for item in results['items']:
            original_text = item['snippet']['topLevelComment']['snippet']['textOriginal']
            if len(original_text) > 5:
                comment_id = item['snippet']['topLevelComment']['id']
                # Check if comment with the same comment ID already exists
                if not any(comment['comment_id'] == comment_id for comment in comments):
                    dict_comment = {
                        'comment_id': comment_id,
                        'text_original': original_text,
                        'video_id': item['snippet']['topLevelComment']['snippet']['videoId'],
                        'author_name': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        'author_cid': item['snippet']['topLevelComment']['snippet']['authorChannelId'],
                        'published_at': item['snippet']['topLevelComment']['snippet']['publishedAt'],
                        'updated_at': item['snippet']['topLevelComment']['snippet']['updatedAt'],
                        'parent_id': '',
                        'label': ''
                    }
                    comments.append(dict_comment)
            if int(item['snippet']['totalReplyCount']) > 0:
                for reply in item['replies']['comments']:
                    reply_text = reply['snippet']['textOriginal']
                    if len(reply_text) > 5:
                        reply_id = reply['id']
                        # Check if reply with the same reply ID already exists
                        if not any(comment['comment_id'] == reply_id for comment in comments):
                            dict_replies = {
                                'comment_id': reply_id,
                                'text_original': reply_text,
                                'video_id': reply['snippet']['videoId'],
                                'parent_id': reply['snippet']['parentId'],
                                'author_name': reply['snippet']['authorDisplayName'],
                                'author_cid': reply['snippet']['authorChannelId'],
                                'published_at': reply['snippet']['publishedAt'],
                                'updated_at': reply['snippet']['updatedAt'],
                                'label': ''
                            }
                            comments.append(dict_replies)

        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = youtube.commentThreads().list(**kwargs).execute()
        else:
            break

    return comments

def sentiment_analyzers(comment):
    sentiment = ''
    compound_score = sentiments.polarity_scores(comment)["compound"]
    if compound_score >= 0.05:
        sentiment = 'Positive'
    elif compound_score <= -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return sentiment

def detect_lang(comment):
    try:
        lang_code = detect(comment)
        if lang_code in ['en', 'ur']:
            return lang_code
    except LangDetectException as e:
        # Handle the exception when no features are detected
        # print(f"Error detecting language: {str(e)}")
        return ""

def comment_cleaning(comment):
    start_cleaning = re.sub(r'http\S+', '', comment)
    start_cleaning = word_tokenize(start_cleaning.lower())
    stop_words = set(stopwords.words('english'))
    start_cleaning = [word for word in start_cleaning if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    start_cleaning = [lemmatizer.lemmatize(word) for word in start_cleaning]
    start_cleaning = ' '.join(start_cleaning)
    start_cleaning = re.sub(r'[@%?&!#$^*:;/\|=-><.]', '', start_cleaning)
    return start_cleaning
