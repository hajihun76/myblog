from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from datetime import datetime, date
import calendar
from collections import Counter
from django.utils import timezone
from .models import BusQueryLog, BusOrderLog
from django.db.models import Q, Count  # ✅ 검색용 추가
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import TemplateView, ListView, RedirectView
from blog.utils.device import is_mobile_request
import random
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from django.contrib.auth.models import User



def has_busorder_permission(user):
    return user.is_superuser or user.has_perm('busorder.can_access_busorder')


# 기준 순번 리스트 (2025년 5월 1일 기준)
BASE_ORDER = [
    8322, 5809, 5857, 8508, 5846, 5876, 5840, 5852, 5810, 5842,
    2700, 5848, 5816, 5829, 2703, 2701, 2698, 2702, 5819, 5838,
    5823, 7309
]

# ✅ 누적 이동 방식으로 달력 생성
def generate_schedule_across_months(base_order, target_year, target_month):
    base_date = datetime(2025, 5, 1)
    schedule = {}
    days_in_month = calendar.monthrange(target_year, target_month)[1]

    for day in range(1, days_in_month + 1):
        target_date = datetime(target_year, target_month, day)
        days_passed = (target_date - base_date).days
        shifted = [
            base_order[(i + 5 * days_passed) % len(base_order)]
            for i in range(len(base_order))
        ]
        schedule[target_date.strftime("%Y-%m-%d")] = shifted

    return schedule

# ✅ 순번 위치 찾기
def get_order(schedule, date, bus_number):
    order_list = schedule.get(date, [])
    try:
        index = order_list.index(bus_number)
        return index + 1
    except ValueError:
        return -1

# ✅ 메인 페이지 뷰
@login_required
@permission_required('busorder.can_access_busorder', raise_exception=True)
def calendar_view(request):
    return render(request, "busorder/calendar.html")

# ✅ 조회 API
@login_required
@permission_required('busorder.can_access_busorder', raise_exception=True)
def order_check(request):
    date = request.GET.get("date")
    bus_number = request.GET.get("bus")
    try:
        bus_number = int(bus_number)
    except:
        return JsonResponse({"result": "버스 번호는 숫자 4자리여야 합니다."})

    try:
        year, month, day = map(int, date.split('-'))
        schedule = generate_schedule_across_months(BASE_ORDER, year, month)
        position = get_order(schedule, date, bus_number)

        if position == -1:
            return JsonResponse({"result": f"{date}에 {bus_number}번 버스를 찾을 수 없습니다."})

        # ✅ 조회 기록 저장
        BusQueryLog.objects.create(
            user=request.user,
            date=date,
            bus_number=bus_number
        )

        return JsonResponse({"result": f"{date}의 {bus_number}번 버스는 {position}번째 순번입니다."})
    except Exception as e:
        return JsonResponse({"result": f"오류 발생: {e}"})
    
@login_required
@permission_required('busorder.can_access_busorder', raise_exception=True)
def query_logs(request):
    logs = BusQueryLog.objects.filter(user=request.user).order_by('-queried_at')[:30]
    return render(request, "busorder/logs.html", {"logs": logs})


@login_required
@permission_required('busorder.can_access_busorder', raise_exception=True)
def query_logs_all(request):
    logs = BusQueryLog.objects.all().order_by('-queried_at')

    date = request.GET.get('date')
    bus_number = request.GET.get('bus_number')

    if date:
        logs = logs.filter(date=date)
    if bus_number:
        try:
            bus_number = int(bus_number)
            logs = logs.filter(bus_number=bus_number)
        except ValueError:
            pass  # 숫자 아닐 경우 무시

    return render(request, "busorder/logs_all.html", {"logs": logs})

@login_required
@permission_required('busorder.can_access_busorder', raise_exception=True)
def stats_view(request):
    year = int(request.GET.get("year", timezone.now().year))
    month = int(request.GET.get("month", timezone.now().month))

    logs = BusQueryLog.objects.filter(date__year=year, date__month=month)
    counts = Counter(log.bus_number for log in logs)

    # 라벨, 값 분리해서 전달
    labels = [str(bus) for bus, _ in sorted(counts.items())]
    values = [count for _, count in sorted(counts.items())]

    return render(request, "busorder/stats.html", {
        "year": year,
        "month": month,
        "labels": labels,
        "values": values
    })

def permission_denied_view(request, exception=None):
    return render(request, "busorder/403.html", status=403)

class BusOrderMainView(LoginRequiredMixin, View):
    def get(self, request):
        if not has_busorder_permission(request.user):
            return redirect('permission_pending')
        if is_mobile_request(request):
            return render(request, 'busorder/mobile_main.html')
        return render(request, 'busorder/desktop_block.html')
    
    def post(self, request):
        if not has_busorder_permission(request.user):
            return redirect('permission_pending')

        selected_date = request.POST.get('selected_date')
        bus_number = request.POST.get('bus_number')

        if not selected_date or not bus_number:
            return redirect('busorder:main')  # 값이 없으면 다시 메인으로
        
        try:
            year, month, day = map(int, selected_date.split('-'))
            schedule = generate_schedule_across_months(BASE_ORDER, year, month)
            bus_number_int = int(bus_number)
            queue_number = get_order(schedule, selected_date, bus_number_int)
        except Exception as e:
            queue_number = -1

        if queue_number == -1:
            return render(request, 'busorder/mobile_main.html', {
                'error_message': f"{selected_date}에 {bus_number}번 버스를 찾을 수 없습니다."
            })

        # ✅ 로그 저장
        BusOrderLog.objects.create(
            user=request.user,
            date=selected_date,
            bus_number=bus_number,
            queue_number=queue_number,
        )

        return render(request, 'busorder/mobile_main.html', {
            'selected_date': selected_date,
            'bus_number': bus_number,
            'queue_number': queue_number,
        })
    
class PermissionPendingView(TemplateView):
    template_name = 'permission_pending.html'

class BusOrderAPI(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        data = request.POST
        date = data.get('date')
        bus_number = data.get('bus_number')

        if not date or not bus_number:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        # 순번 랜덤 생성 (실제로는 로직 추가 가능)
        order = random.randint(1, 50)

        log = BusOrderLog.objects.create(
            user=request.user,
            date=date,
            bus_number=bus_number,
            order_number=order,
        )

        return JsonResponse({'order': log.order_number})
    
class BusOrderHistoryView(LoginRequiredMixin, ListView):
    model = BusOrderLog
    template_name = 'busorder/admin_history.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']

    def get_queryset(self):
        return BusOrderLog.objects.filter(user=self.request.user)
    
class BusOrderAdminLogView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BusOrderLog
    template_name = 'busorder/admin_log.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']

    def test_func(self):
        return self.request.user.is_staff or self.request.user.has_perm('busorder.can_access_all_logs')

    def get_queryset(self):
        queryset = super().get_queryset()

        # ✅ 필터링: GET 파라미터로 받은 값으로 필터
        selected_date = self.request.GET.get('selected_date')
        bus_number = self.request.GET.get('bus_number')

        if selected_date:
            queryset = queryset.filter(selected_date=selected_date)
        if bus_number:
            queryset = queryset.filter(bus_number__icontains=bus_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ✅ 필터 유지용 context
        context['selected_date'] = self.request.GET.get('selected_date', '')
        context['bus_number'] = self.request.GET.get('bus_number', '')
        return context
    
class BusOrderMonthlyStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.has_perm('busorder.can_access_all_logs')

    def get(self, request):
        from busorder.models import BusOrderLog  # 위치에 따라 수정

        logs = (
            BusOrderLog.objects
            .annotate(month=TruncMonth('timestamp'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # 차트용 데이터 추출
        labels = [log['month'].strftime('%Y-%m') for log in logs]
        data = [log['count'] for log in logs]

        return render(request, 'busorder/monthly_stats.html', {
            'labels': labels,
            'data': data,
        })

@method_decorator(staff_member_required, name='dispatch')
class MonthlyStatsView(View):
    def get(self, request):
        # 월별로 순번 조회 수를 집계
        monthly_counts = (
            BusOrderLog.objects
            .annotate(month=TruncMonth('timestamp'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        return render(request, 'busorder/monthly_stats.html', {
            'monthly_counts': monthly_counts
        })
    
@method_decorator(login_required, name='dispatch')
class MyBusOrderHistoryView(View):
    def get(self, request):
        logs = (
            BusOrderLog.objects
            .filter(user=request.user)
            .order_by('-timestamp')
        )
        return render(request, 'busorder/my_history.html', {
            'logs': logs
        })
    
class QueryHistoryView(LoginRequiredMixin, ListView):
    model = BusOrderLog
    template_name = 'busorder/query_history.html'
    context_object_name = 'logs'

    def get_queryset(self):
        return BusOrderLog.objects.filter(user=self.request.user).order_by('-timestamp')
    