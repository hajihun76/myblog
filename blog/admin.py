from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm, DateInput

from .models import User, PostList, PostListPics

class PostListAdminForm(ModelForm):
    class Meta:
        model = PostList
        fields = '__all__'
        widgets = {
            'created_at': DateInput(attrs={'type': 'date'}),
        }

@admin.register(PostList)
class PostListAdmin(admin.ModelAdmin):
    form = PostListAdminForm

admin.site.register(User, UserAdmin)
UserAdmin.fieldsets += (('Custom fields', {'fields': ('nickname', 'profile_pic', 'intro')}),)
admin.site.register(PostListPics)
