from django.urls import path

from youtube_app import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('fetch/', views.insert_url, name='cfetch'),
    path('analysis/', views.sanalysis, name='sanalysis'),
    path('detection/', views.sdetection, name='sdetection'),
    path('about/', views.aboutus, name='aboutus'),
    path('model/', views.models, name='models'),
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    # other URL patterns
    path('fetch-comm/', views.fetch_comments, name='fetch-comm'),
    path('eng-comments/<str:video_id>/', views.fetch_eng_comments, name='fetch-eng'),
    path('emoji-comments/<str:video_id>/', views.fetch_emoji_comments, name='fetch-emoji'),
    path('abc/', views.abc, name='abc')
]


