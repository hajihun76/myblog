# accounts/views.py
from allauth.account.views import LoginView, SignupView
from blog.utils.device import is_mobile_request
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    def get_template_names(self):
        if is_mobile_request(self.request):
            return ['accounts/mobile_login.html']
        return ['account/login.html']
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if is_mobile_request(self.request):
            return redirect('/busorder/')
        return response


class CustomSignupView(SignupView):
    def get_template_names(self):
        if is_mobile_request(self.request):
            return ['accounts/mobile_signup.html']
        return ['account/signup.html']
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if is_mobile_request(self.request):
            return redirect('/busorder/')
        return response