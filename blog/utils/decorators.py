from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect

def modal_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'authenticated': False}, status=401)
            else:
                return redirect('account_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
