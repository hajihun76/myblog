from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from allauth.account.views import PasswordChangeView
from .models import Post, PostList, PostListPics
from .forms import PostForm, PostListForm, PostListPicsForm

# 기본 Allauth
def index(request):
    return render(request, 'blog/index.html')

class CustomPasswordChangeView(PasswordChangeView):
    def get_success_url(self):
        return reverse('index')

# 갤러리 목록
class GalleryListView(ListView):
    model = PostList
    template_name = 'blog/gallery/gallery_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']

class PostPicsDetailView(DetailView):
    model = PostListPics
    template_name = 'blog/gallery/pics_detail.html'
    context_object_name = 'pic'
    pk_url_kwarg = 'pics_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exif'] = self.object.metadata or {}
        return context

class PostListPicsListView(ListView):
    model = PostListPics
    template_name = 'blog/gallery/post_pics_detail.html'
    context_object_name = 'post_list_pics'
    pk_url_kwarg = 'post_list_id'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(post_list_id=self.kwargs['post_list_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ① 부모 갤러리 객체를 넘겨 줍니다
        context['post_list'] = get_object_or_404(
            PostList, pk=self.kwargs['post_list_id']
        )
        return context

class PostListCreateView(CreateView):
    model = PostList
    form_class = PostListForm
    template_name = 'blog/gallery/post_list_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('gallery_list')

class PostListUpdateView(UpdateView):
    model = PostList
    form_class = PostListForm
    template_name = 'blog/gallery/post_list_form.html'
    pk_url_kwarg = 'post_list_id'

    def get_success_url(self):
        return reverse('gallery_list')

class PostListDeleteView(DeleteView):
    model = PostList
    template_name = 'blog/post_confirm_delete.html'
    pk_url_kwarg = 'post_list_id'

    def get_success_url(self):
        return reverse('gallery_list')

class PostListPicsCreateView(CreateView):
    model = PostListPics
    form_class = PostListPicsForm
    template_name = 'blog/gallery/post_list_pics_form.html'

    def form_valid(self, form):
        form.instance.post_list_id = self.kwargs['post_list_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('post_list_detail', kwargs={'post_list_id': self.kwargs['post_list_id']})

class PostListPicsUpdateView(UpdateView):
    model = PostListPics
    form_class = PostListPicsForm
    template_name = 'blog/gallery/post_list_pics_form.html'
    pk_url_kwarg = 'pics_id'

    def get_success_url(self):
        return reverse('post_list_detail', kwargs={'post_list_id': self.kwargs['post_list_id']})

# 맛집 여행 목록
class TourListView(ListView):
    model = Post
    template_name = 'blog/tour/tour_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']

# Community 게시판
class CommunityListView(ListView):
    model = Post
    template_name = 'blog/community/community_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']

# class PostCreateView(CreateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'blog/post_form.html'

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         return reverse('post_detail', kwargs={'post_id': self.object.id})

