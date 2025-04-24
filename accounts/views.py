# accounts/views.py
from allauth.account.views import LoginView, SignupView
from django.shortcuts import redirect
from blog.utils.device import is_mobile_request
from django.urls import reverse
from django.views.generic import TemplateView


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
    
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.has_perm('busorder.can_access_busorder'):
            return reverse('busorder:main')
        else:
            return reverse('permission_pending')


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

    def get_success_url(self):
        user = self.request.user
        if not user.has_perm('busorder.can_access_busorder'):
            return reverse('permission_pending')
        return '/busorder/'
    
class PermissionPendingView(TemplateView):
    template_name = 'accounts/permission_pending.html'