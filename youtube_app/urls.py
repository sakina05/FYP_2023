from django.urls import path

from youtube_app import views

urlpatterns = [
    path('homepage', views.homepage, name='homepage'),
    path('fetch/', views.cfetch, name='cfetch'),
    path('analysis/', views.sanalysis, name='sanalysis'),
    path('detection/', views.sdetection, name='sdetection'),
    path('about/', views.aboutus, name='aboutus'),
    path('model/', views.models, name='models'),
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup')

]