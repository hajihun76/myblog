# blog/templatetags/exif_extras.py

from django import template

register = template.Library()

@register.filter
def rational_to_float(value, decimal_places=1):
    """
    IFDRational 튜플(value[0], value[1])을 나누어
    소수점 decimal_places자리까지 포맷한 문자열을 반환.
    """
    try:
        num, den = value
        result = num / den
        # "%.1f"처럼 포맷 문자열 생성
        format_str = f"%.{decimal_places}f"
        return format_str % result
    except Exception:
        return ''
