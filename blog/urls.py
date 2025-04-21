from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # 갤러리 목록
    path('gallery/lists/', views.GalleryListView.as_view(), name='gallery_list'),
    # PostList 갤러리
    path('post_lists/<int:post_list_id>/', views.PostListPicsListView.as_view(), name='post_list_detail'),
    # 갤러리 목록 생성
    path('posts/lists/new/', views.PostListCreateView.as_view(), name='post_list_create'),
    # PostList 갤러리 생성
    path('posts/lists/<int:post_list_id>/pics/new/', views.PostListPicsCreateView.as_view(), name='post_list_pics_create'),
    # PostList 갤러리 상세 페이지
    path('posts/lists/<int:post_list_id>/pics/<int:pics_id>/', views.PostPicsDetailView.as_view(), name='post_pics_detail'),

    # 맛집, 여행지 목록
    path('tour/lists/', views.TourListView.as_view(), name='tour_list'),

    # Community 게시판
    path('community/', views.CommunityListView.as_view(), name='community_list'),
]