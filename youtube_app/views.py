from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponseRedirect
from django.shortcuts import render

from youtube_app.forms import BasicRegForm, LoginForm


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
            username = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            user = EmailBackend.authenticate(request, username=username, password=password)
            if user is not None:
                print("Login success")
                return HttpResponseRedirect('/ahp/index/')
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
            reg.is_active = False
            password = reg.password
            reg.set_password(password)
            reg.save()
            messages.info(request, 'Please confirm your email address to complete the registration')
            return HttpResponseRedirect('/ahp/index/')
        else:
            context['teacher_form_error'] = 'True'
            messages.error(request, "ERROR! while saving info please try again")
    context['reg_form'] = reg_form
    context['current_page'] = 'signup'
    return render(request, 'signup.html', context)

