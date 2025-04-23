from django import forms
from .models import User, PostList, PostListPics

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