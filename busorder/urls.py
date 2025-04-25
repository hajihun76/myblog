from django.urls import path
from . import views
from .views import (
    BusOrderMainView, PermissionPendingView, BusOrderAPI,
    BusOrderAdminLogView, MonthlyStatsView, MyBusOrderHistoryView,
    BusOrderHistoryView, QueryHistoryView, BusOrderMonthlyStatsView,
)

app_name = 'busorder'

urlpatterns = [
    path("calendar/", views.calendar_view, name="calendar-view"),
    path("order-check/", views.order_check, name="order-check"),
    path("logs/", views.query_logs, name="query_logs"),  # 개인 전용
    path("logs/all/", views.query_logs_all, name="query_logs_all"),  # 관리자 전용
    path("stats/", views.stats_view, name="busorder_stats"),

    path('', BusOrderMainView.as_view(), name='main'),
    path('permission-pending/', PermissionPendingView.as_view(), name='permission_pending'),

    path('api/log/', BusOrderAPI.as_view(), name='api_log'),

    # ✅ 이름 충돌 정리
    path('my-history/', MyBusOrderHistoryView.as_view(), name='my_history'),
    path('admin-history/', BusOrderHistoryView.as_view(), name='admin_history'),
    path('query-history/', QueryHistoryView.as_view(), name='query_history'),

    # ✅ 통계
    path('stats/monthly/', BusOrderMonthlyStatsView.as_view(), name='monthly_stats'),
    path('monthly-stats/', MonthlyStatsView.as_view(), name='monthly_stats_old'),
]
