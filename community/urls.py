from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='community_list'),
    path('new/', views.PostCreateView.as_view(), name='community_create'),
    path('<int:post_id>/', views.PostDetailView.as_view(), name='community_detail'),
    path('<int:post_id>/edit/', views.PostUpdateView.as_view(), name='community_update'),
    path('<int:post_id>/delete/', views.PostDeleteView.as_view(), name='community_delete'),
    path('comments/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('posts/<int:post_id>/comments/', views.CommentCreateView.as_view(), name='comment_create'),
]
