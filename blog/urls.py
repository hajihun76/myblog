from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),

    # 프로필 페이지
    path('set-profile/', views.ProfileSetView.as_view(), name='profile-set'),
    path('users/<int:user_id>/', views.ProfileView.as_view(), name='profile'),
    path('edit-profile/', views.ProfileUpdateView.as_view(), name='profile-update'),

    # 갤러리 목록 CRUD
    path('gallery/lists/', views.GalleryListView.as_view(), name='gallery_list'),
    path('posts/lists/new/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/lists/<int:post_list_id>/edit/', views.PostListUpdateView.as_view(), name='post_list_edit'),
    path('posts/lists/<int:post_list_id>/delete/', views.PostListDeleteView.as_view(), name='post_list_delete'),

    # PostListPics 갤러리 CRUD
    path('post_lists/<int:post_list_id>/', views.PostListPicsListView.as_view(), name='post_list_detail'),
    path('posts/lists/<int:post_list_id>/pics/new/', views.PostListPicsCreateView.as_view(), name='post_list_pics_create'),
    path('posts/lists/<int:post_list_id>/pics/<int:pics_id>/edit/', views.PostListPicsUpdateView.as_view(), name='post_list_pics_edit'),
    path('posts/lists/<int:post_list_id>/pics/<int:pics_id>/delete/', views.PostListPicsDeleteView.as_view(), name='post_list_pics_delete'),

    # PostList 갤러리 상세 페이지
    path('posts/lists/<int:post_list_id>/pics/<int:pics_id>/', views.PostPicsDetailView.as_view(), name='post_pics_detail'),
]