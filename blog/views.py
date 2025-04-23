from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from allauth.account.views import PasswordChangeView
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from .models import User, PostList, PostListPics
from .forms import PostListForm, PostListPicsForm, ProfileForm

# 기본 Allauth
def index(request):
    return render(request, 'blog/index.html')

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def get_success_url(self):
        return reverse('account_reset_password_from_key_done')
    
# 프로필 뷰
class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile/profile.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile_user'

class ProfileSetView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/profile/profile_set_form.html'

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('index')
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/profile/profile_update_form.html'

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('profile', kwargs={'user_id': self.request.user.id})


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

class PostListPicsListView(LoginRequiredMixin, ListView):
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

class PostListCreateView(LoginRequiredMixin, CreateView):
    model = PostList
    form_class = PostListForm
    template_name = 'blog/gallery/post_list_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('gallery_list')

class PostListUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PostList
    form_class = PostListForm
    template_name = 'blog/gallery/post_list_form.html'
    pk_url_kwarg = 'post_list_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # URL kwargs에서 post_list_id를 빼와 원본 PostList 객체 조회
        ctx['post_list'] = get_object_or_404(
            PostList, pk=self.kwargs['post_list_id']
        )
        return ctx

    # 익명(unauthenticated) 사용자도 403을 받도록
    redirect_unauthenticated_users = False
    # 인증됐는데 test_func()를 통과 못 하면 403을 띄움
    raise_exception = True

    def get_success_url(self):
        return reverse('gallery_list')
    
    def test_func(self, user):
        post = self.get_object()
        return post.author == user

class PostListDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PostList
    template_name = 'blog/gallery/post_confirm_delete.html'
    pk_url_kwarg = 'post_list_id'

    # 익명(unauthenticated) 사용자도 403을 받도록
    redirect_unauthenticated_users = False
    # 인증됐는데 test_func()를 통과 못 하면 403을 띄움
    raise_exception = True

    def get_success_url(self):
        return reverse('gallery_list')
    
    def test_func(self, user):
        post = self.get_object()
        return post.author == user

class PostListPicsCreateView(LoginRequiredMixin, CreateView):
    model = PostListPics
    form_class = PostListPicsForm
    template_name = 'blog/gallery/post_list_pics_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # URL에 있는 post_list_id 로 PostList 가져오기
        post_list = get_object_or_404(
            PostList, pk=self.kwargs['post_list_id']
        )
        context['post_list'] = post_list
        return context

    def form_valid(self, form):
        form.instance.post_list_id = self.kwargs['post_list_id']
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('post_list_detail', kwargs={'post_list_id': self.kwargs['post_list_id']})

class PostListPicsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PostListPics
    form_class = PostListPicsForm
    template_name = 'blog/gallery/post_list_pics_form.html'
    pk_url_kwarg = 'pics_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # URL kwargs에서 post_list_id를 빼와 원본 PostList 객체 조회
        ctx['post_list'] = get_object_or_404(
            PostList, pk=self.kwargs['post_list_id']
        )
        return ctx

    redirect_unauthenticated_users = False
    raise_exception = True

    def get_success_url(self):
        return reverse('post_list_detail', kwargs={'post_list_id': self.kwargs['post_list_id']})
    
    def test_func(self, user):
        pic = self.get_object()
        return pic.author == user

class PostListPicsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PostListPics
    template_name = 'blog/gallery/post_pic_confirm_delete.html'
    pk_url_kwarg = 'pics_id'

    redirect_unauthenticated_users = False
    raise_exception = True

    def get_success_url(self):
        return reverse('post_list_detail', kwargs={'post_list_id': self.kwargs['post_list_id']})
    
    def test_func(self, user):
        pic = self.get_object()
        return pic.author == user