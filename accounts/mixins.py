from django.contrib.auth.mixins import AccessMixin
from django.http import JsonResponse
from django.shortcuts import redirect

class ModalLoginRequiredMixin(AccessMixin):
    """로그인 안 된 경우, Ajax 요청이면 JSON 응답, 일반 요청이면 홈으로 보내기"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'authenticated': False}, status=401)
            else:
                return redirect('account_login')
        
        # 로그인 되어있으면 반드시 super().dispatch() 호출
        return super().dispatch(request, *args, **kwargs)