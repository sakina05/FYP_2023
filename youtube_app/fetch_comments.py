import re
import emoji
# from emot.emo_unicode import UNICODE_EMOJI
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect, LangDetectException
from langdetect import detect

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
                        'label': '',
                        'spamlabel':''
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
                                'label': '',
                                'spamlabel': ''
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
        if lang_code in ['en']:
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
    start_cleaning = ' '.join(start_cleaning)
    start_cleaning = re.sub(r'[@%?&!#$^*::/\|=-><.]', '', start_cleaning)
    characters = [chr for chr in comment]
    emoji_list = [c for c in comment if c in emoji.UNICODE_EMOJI["en"]]
    clean_text = ''.join([c for c in characters if c not in emoji_list])
    clean_emoji = " ".join([chr for chr in comment if any(i in chr for i in emoji_list)])
    return clean_text, clean_emoji

def find_emoji_text(comment):
    emoji_list = [c for c in comment if c in emoji.UNICODE_EMOJI["en"]]
    clean_emoji = " ".join([chr for chr in comment if any(i in chr for i in emoji_list)])
    return clean_emoji

def is_english(comment):
    try:
        return detect(comment) == 'en'
    except:
        return False

def spamcomment_cleaning(comment):
    # Check if the comment is in English
    if not is_english(comment):
        return None

    # Remove extra whitespaces and newlines
    cleaned_comment = re.sub(r'\s+', ' ', comment).strip()

    # Tokenize the comment and convert to lowercase
    words = word_tokenize(cleaned_comment.lower())

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Reconstruct the cleaned comment
    cleaned_comment = ' '.join(words)

    return cleaned_comment


def label_spam_comments(comment):
    spam_words = ['win', 'prize', 'cash', 'money', 'lottery', 'free', 'offer', 'gift', 'deal', 'sale']
    spam_emojis = ['\U0001F4B0', '\U0001F381', '\U0001F4B8', '\U0001F4B5', '\U0001F3AF', '\U0001F195', '\U0001F381', '\U0001F381', '\U0001F4B0']
    spam_chars = ['$', '%', '!', '@']
    spam_urls = ['http', 'https', 'www.', 'bit.ly']
    sid = SentimentIntensityAnalyzer()

    # Sentiment Analysis
    sentiment = sid.polarity_scores(comment)
    if sentiment['compound'] < 0:

    # Check for spam words
        if any(word in comment.lower() for word in spam_words):
            return 'spam'

    # Check for spam emojis
        if any(emoji in comment for emoji in spam_emojis):
            return 'spam'

    # Check for spam characters
        if any(char in comment for char in spam_chars):
            return 'spam'

    # Check for spam URLs
        if any(url in comment.lower() for url in spam_urls):
            return 'spam'

        return 'spam'
    else: # Otherwise, label as ham
        return 'ham'

