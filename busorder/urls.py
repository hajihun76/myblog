from django.urls import path
from . import views
from .views import BusOrderMainView, PermissionPendingView, BusOrderAPI, BusOrderHistoryView, MonthlyStatsView, MyBusOrderHistoryView

app_name = 'busorder'

urlpatterns = [
    path("calendar/", views.calendar_view, name="calendar-view"),
    path("order-check/", views.order_check, name="order-check"),
    path("logs/", views.query_logs, name="query-logs"),  # 개인 전용
    path("logs/all/", views.query_logs_all, name="query-logs-all"),  # 관리자 전용
    path("stats/", views.stats_view, name="busorder-stats"),
    path('', BusOrderMainView.as_view(), name='main'),
    path('permission-pending/', PermissionPendingView.as_view(), name='permission_pending'),
    path('api/log/', BusOrderAPI.as_view(), name='api_log'),  # POST 전용 API
    path('history/', BusOrderHistoryView.as_view(), name='history'),
    path('admin-log/', views.BusOrderAdminLogView.as_view(), name='admin_log'),
    path('stats/monthly/', views.BusOrderMonthlyStatsView.as_view(), name='monthly_stats'),
    path('monthly-stats/', MonthlyStatsView.as_view(), name='monthly_stats'),
    path('my-history/', MyBusOrderHistoryView.as_view(), name='history'),
    path('history/', views.QueryHistoryView.as_view(), name='query-logs'), 
]