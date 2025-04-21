# blog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import PostList

class PostListSitemap(Sitemap):
    changefreq = "weekly"  # 업데이트 주기
    priority = 0.8

    def items(self):
        return PostList.objects.all()

    def lastmod(self, obj):
        return obj.created_at
