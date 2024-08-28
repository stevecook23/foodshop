from allauth.account.forms import SignupForm, LoginForm

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs['placeholder'] = ''
            field.widget.attrs['class'] = 'form-control'
            field.label = field.label.capitalize()
            
class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs['placeholder'] = ''
            field.widget.attrs['class'] = 'form-control'
            field.label = field.label.capitalize()