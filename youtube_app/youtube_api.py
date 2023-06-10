import os
import googleapiclient.discovery
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Set up YouTube Data API credentials
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


def get_video_comments(video_url):
    # Extract video ID from the YouTube URL
    video_id = extract_video_id(video_url)

    # Create YouTube Data API client
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyAG5WGAxvhSWQOeQ2l3GerfKXsuUdtjKTs"  # Replace with your own YouTube API key
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

    # Call the API to fetch video comments
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    ).execute()

    comments = []
    for item in response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        # Check if comment is in English
        if is_english(comment):
            # Clean the comment
            cleaned_comment = clean_comment(comment)
            comments.append(cleaned_comment)

    return comments


def extract_video_id(url):
    video_id = None
    try:
        # Extract video ID from different types of YouTube URLs
        if 'youtube.com' in url:
            video_id = url.split('v=')[1].split('&')[0]
        elif 'youtu.be' in url:
            video_id = url.split('/')[-1].split('?')[0]
        elif 'embed' in url:
            video_id = url.split('/')[-1].split('?')[0]
    except IndexError:
        pass
    return video_id


def is_english(text):
    # Check if the majority of characters in the text are in the English alphabet
    english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
    return english_chars / len(text) > 0.5


def clean_comment(comment):
    # Remove URLs from the comment
    comment = re.sub(r'http\S+|www\S+', '', comment)

    # Tokenize the comment
    tokens = word_tokenize(comment)

    # Remove stopwords from the tokens
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.lower() not in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Remove special characters and convert to lowercase
    tokens = [re.sub(r'[^a-zA-Z0-9]', '', token.lower()) for token in tokens if token.isalnum()]

    # Join the tokens back into a cleaned comment
    cleaned_comment = ' '.join(tokens)

    return cleaned_comment
