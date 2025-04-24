from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from datetime import datetime, date
import calendar
from collections import Counter
from django.utils import timezone
from .models import BusQueryLog
from django.db.models import Q  # ✅ 검색용 추가

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
    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('busorder.can_access'):  # 또는 사용자 필드 검사
            return render(request, 'busorder/permission_pending.html')  # 별도 템플릿
        return render(request, 'busorder/main.html')