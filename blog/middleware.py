from django.urls import reverse
from django.shortcuts import redirect

class ProfileSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        user = request.user
        path = request.path_info

        # 1) 로그인했고, 닉네임이 없고,
        # 2) profile-set 뷰가 아니고,
        # 3) skip_profile 파라미터가 없을 때만 리다이렉트
        if (
            user.is_authenticated
            and not user.nickname
            and path != reverse('profile-set')
            and request.GET.get('skip_profile') != '1'
        ):
            return redirect('profile-set')
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response