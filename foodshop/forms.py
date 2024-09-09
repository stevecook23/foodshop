"""Forms for the custom signup and login pages."""
from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.contrib.auth import get_user_model


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs['placeholder'] = ''
            field.widget.attrs['class'] = 'form-control'
            field.label = field.label.capitalize()

    def clean_username(self):
        username = self.cleaned_data['username']
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs['placeholder'] = ''
            field.widget.attrs['class'] = 'form-control'
            field.label = field.label.capitalize()
