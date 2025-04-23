from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from .forms import CommentForm, PostForm

class PostListView(ListView):
    model = Post
    template_name = 'community/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('-is_notice', '-created_at') # 공지 -> 최신순
        keyword = self.request.GET.get('q', '')
        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword) | 
                Q(content__icontains=keyword) | 
                Q(author__nickname__icontains=keyword)
            )
        return qs.order_by('-is_notice', '-created_at')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'community/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user

        # ✅ 관리자가 아닌 경우 공지글 체크 무시
        if not self.request.user.is_staff:
            form.instance.is_notice = False

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('community_list')

class PostDetailView(DetailView):
    model = Post
    template_name = 'community/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        post.views += 1
        post.save(update_fields=['views'])
        return post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect('community_detail', post_id=self.object.pk)
        return self.render_to_response(self.get_context_data(comment_form=form))

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm  # ✅ PostForm 사용
    template_name = 'community/post_form.html'
    pk_url_kwarg = 'post_id'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ✅ user 전달 (폼에서 is_superuser 체크용)
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('community_detail', kwargs={'post_id': self.object.id})

    def test_func(self):
        return self.get_object().author == self.request.user

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'community/post_confirm_delete.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('community_list')
    
    def test_func(self):
        return self.get_object().author == self.request.user

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'community/comment_form.html'

    def get_success_url(self):
        return reverse('community_detail', kwargs={'post_id': self.object.post.pk})

    def test_func(self):
        return self.request.user == self.get_object().author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'community/comment_confirm_delete.html'

    def get_success_url(self):
        return reverse('community_detail', kwargs={'post_id': self.object.post.pk})

    def test_func(self):
        return self.request.user == self.get_object().author

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user

        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            parent_comment = get_object_or_404(Comment, pk=parent_id)
            form.instance.parent = parent_comment

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('community_detail', kwargs={'post_id': self.kwargs['post_id']})