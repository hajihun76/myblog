# accounts/views.py
from allauth.account.views import LoginView, SignupView
from django.shortcuts import redirect
from blog.utils.device import is_mobile_request
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.urls import resolve


class CustomLoginView(LoginView):
    def get_template_names(self):
        if is_mobile_request(self.request):
            return ['accounts/mobile_login.html']
        return ['account/login.html']

    def get_success_url(self):
        user = self.request.user
        next_url = self.request.GET.get('next')

        # ✅ 모바일이면 무조건 /busorder/로 리디렉션
        if is_mobile_request(self.request):
            if user.is_authenticated and user.has_perm('busorder.can_access_busorder'):
                return reverse('busorder:main')
            return reverse('permission_pending')

        # ✅ 컴퓨터에서 접근한 경우는 next_url 처리
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            try:
                resolve(next_url)
                return next_url
            except:
                pass

        return settings.LOGIN_REDIRECT_URL  # 보통은 '/'


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