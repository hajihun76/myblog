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

        # ✅ 권한이 있는 경우 처리
        if user.is_authenticated and user.has_perm('busorder.can_access_busorder'):
            if is_mobile_request(self.request):
                return reverse('busorder:main')  # 모바일은 busorder 메인
            return reverse('permission_pending')  # PC는 안내 페이지

        # ✅ next가 유효하고 접근 가능한 URL인지 확인
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            try:
                resolve(next_url)  # URL이 실제로 존재하는지 확인
                return next_url
            except:
                pass  # 유효하지 않으면 무시하고 fallback

        # ✅ 기본 리디렉션 경로
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