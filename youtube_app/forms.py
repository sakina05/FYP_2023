import django
from django import forms
from .models import YoutubeVideoId
from .models import User

Customer = 1
CT_Provider = 0
CITY_NAME_CHOICES = (
    (Customer, 'Customer'),
    (CT_Provider, 'CT Provider')
)
class BasicRegForm(django.forms.ModelForm):
    username = django.forms.CharField(
        min_length=4, max_length=15,
        widget=django.forms.TextInput(attrs={'class': 'input', 'placeholder': 'username', 'style': 'color: lightgrey;'})
    )
    email = django.forms.EmailField(
        min_length=6, max_length=40,
        widget=django.forms.TextInput(attrs={'class': 'input', 'placeholder': '@gmail.com', 'style': 'color: lightgrey;'})
    )
    password = django.forms.CharField(
        min_length=6, max_length=20,
        widget=django.forms.PasswordInput(render_value=False, attrs={'placeholder': 'password', 'class': 'input', 'style': 'color: white;'})
    )

    confirm_password = django.forms.CharField(
        widget=django.forms.PasswordInput(attrs={'placeholder': 'RepeatPassword', 'class': 'input', 'style': 'color: white;'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise django.forms.ValidationError("Email already exists")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.data['confirm_password']
        if password != confirm_password:
            raise django.forms.ValidationError("password does not matched")
        return password

class LoginForm(django.forms.Form):
    email = forms.EmailField(
        min_length=6, max_length=40,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        min_length=6, max_length=20,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )

class YoutubeUrlForm(forms.Form):
    video_id = forms.CharField(
        min_length=10, max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control px-4', 'placeholder': 'Enter Urls here'})
    )

    def clean_video_id(self):
        video_url = self.cleaned_data['video_id']
        if YoutubeVideoId.objects.filter(video_url=video_url).exists():
            raise forms.ValidationError("Video url already exists")
        return video_url


# class SentimentAnalyzeForm(forms.Form):
#     input_text = forms.CharField(
#         min_length=10, max_length=100,
#         widget=forms.TextInput(attrs={'class': 'form-control px-4', 'placeholder': 'Enter Text here'})
#     )

class SentimentAnalyzeForm(forms.Form):
    input_text = forms.CharField(
        min_length=10, max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control px-4', 'placeholder': 'Enter Text here'})
    )

from django import forms

class SpamDetectionForm(forms.Form):
    input_text = forms.CharField(
        max_length=500, min_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control px-4', 'placeholder': 'Enter Text here'})
    )




