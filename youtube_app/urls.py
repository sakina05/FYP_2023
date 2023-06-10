from django.urls import path
from .views import fetch_comments
from youtube_app import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('fetch/', views.cfetch, name='cfetch'),
    path('analysis/', views.sanalysis, name='sanalysis'),
    path('detection/', views.sdetection, name='sdetection'),
    path('about/', views.aboutus, name='aboutus'),
    path('model/', views.models, name='models'),
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    # other URL patterns
    path('commentfetch/', views.fetch_comments, name='fetch_comments'),
    path('save-csv/', views.save_csv, name='save_csv'),
    path('clean-comments/', views.clean_comments, name='clean_comments')

]


