# blog/utils/device.py
def is_mobile_request(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = ['iphone', 'android', 'blackberry', 'windows phone']
    return any(keyword in user_agent for keyword in mobile_keywords)
