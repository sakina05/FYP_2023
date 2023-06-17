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
        widget=django.forms.TextInput(attrs={'class': 'input', 'placeholder': 'User Name'})
    )
    email = django.forms.EmailField(
        min_length=6, max_length=40,
        widget=django.forms.TextInput(attrs={'class': 'input', 'placeholder': 'Email Address'})
    )
    password = django.forms.CharField(
        min_length=6, max_length=20,
        widget=django.forms.PasswordInput(render_value=False, attrs={'placeholder': 'Password', 'class': 'input'})
    )

    confirm_password = django.forms.CharField(
        widget=django.forms.PasswordInput(attrs={'placeholder': 'Repeat Password', 'class': 'input'})
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
        widget=forms.TextInput(attrs={'class': '', 'placeholder': 'Enter URLs here'})
    )





