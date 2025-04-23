from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import User, Post, PostList, PostListPics

class PostForm(forms.ModelForm):
    content = forms.CharField(label='본문', widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = Post
        fields = ['title', 'place', 'place_link', 'content']

class PostListForm(forms.ModelForm):
    created_at = forms.DateField(label='작성일', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = PostList
        fields = ['title', 'thumb', 'content', 'created_at']

class PostListPicsForm(forms.ModelForm):
    class Meta:
        model = PostListPics
        fields = ['content', 'image']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'profile_pic', 'intro']
        widgets = {
            'intro': forms.Textarea,
        }