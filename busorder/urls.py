from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendar_view, name="calendar-view"),
    path("order-check/", views.order_check, name="order-check"),
    path("logs/", views.query_logs, name="query-logs"),  # 개인 전용
    path("logs/all/", views.query_logs_all, name="query-logs-all"),  # 관리자 전용
    path("stats/", views.stats_view, name="busorder-stats"),
]