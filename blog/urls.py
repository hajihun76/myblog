from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 갤러리 목록 CRUD
    path('gallery/lists/', views.GalleryListView.as_view(), name='gallery_list'),
    path('posts/lists/new/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/lists/<int:post_list_id>/edit/', views.PostListUpdateView.as_view(), name='post_list_edit'),
    path('posts/lists/<int:post_list_id>/delete/', views.PostListDeleteView.as_view(), name='post_list_delete'),

    # PostListPics 갤러리 CRUD
    path('post_lists/<int:post_list_id>/', views.PostListPicsListView.as_view(), name='post_list_detail'),
    path('posts/lists/<int:post_list_id>/pics/new/', views.PostListPicsCreateView.as_view(), name='post_list_pics_create'),
    path('posts/lists/<int:post_list_id>/pics/<int:pics_id>/edit/', views.PostListPicsUpdateView.as_view(), name='post_list_pics_edit'),

    # PostList 갤러리 상세 페이지
    path('posts/lists/<int:post_list_id>/pics/<int:pics_id>/', views.PostPicsDetailView.as_view(), name='post_pics_detail'),

    # 맛집, 여행지 목록
    path('tour/lists/', views.TourListView.as_view(), name='tour_list'),

    # Community 게시판
    path('community/', views.CommunityListView.as_view(), name='community_list'),
]