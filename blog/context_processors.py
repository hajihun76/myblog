# blog/context_processors.py

from allauth.account.forms import LoginForm, SignupForm

def login_form(request):
    return {'form': LoginForm()}

def signup_form(request):
    return {
        'signup_form': SignupForm()
    }
