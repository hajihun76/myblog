# accounts/views.py
from allauth.account.views import LoginView, SignupView
from django.shortcuts import redirect
from blog.utils.device import is_mobile_request
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.utils.http import url_has_allowed_host_and_scheme



class CustomLoginView(LoginView):
    def get_template_names(self):
        if is_mobile_request(self.request):
            return ['accounts/mobile_login.html']
        return ['account/login.html']

    def get_success_url(self):
        user = self.request.user
        next_url = self.request.GET.get('next')

        if user.is_authenticated and user.has_perm('busorder.can_access_busorder'):
            # 모바일이면 busorder 메인으로, 아니면 권한 안내 페이지로
            if is_mobile_request(self.request):
                return reverse('busorder:main')
            return reverse('permission_pending')
        
        # 그 외에는 next 값이 유효하면 리디렉션
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url

        return settings.LOGIN_REDIRECT_URL


class CustomSignupView(SignupView):
    def get_template_names(self):
        if is_mobile_request(self.request):
            return ['accounts/mobile_signup.html']
        return ['account/signup.html']

    def form_valid(self, form):
        # ✅ 먼저 회원가입 처리
        response = super().form_valid(form)

        # ✅ 이후 로그인된 사용자 기준 리디렉션 분기
        user = self.request.user
        if user.is_authenticated and user.has_perm('busorder.can_access_busorder'):
            return redirect('busorder:main')
        else:
            return redirect('permission_pending')

        return response
    
class PermissionPendingView(TemplateView):
    template_name = 'accounts/permission_pending.html'