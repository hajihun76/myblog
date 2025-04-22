from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image, ExifTags
from PIL.TiffImagePlugin import IFDRational
from io import BytesIO
import os
from PIL import Image
from .validators import validate_no_special_characters, validate_place_link

class User(AbstractUser):
    nickname = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        validators=[validate_no_special_characters],
        error_messages={'unique': '이미 사용중인 닉네임입니다.'},
    )

    def __str__(self):
        return self.email

class PostList(models.Model):
    title = models.CharField(max_length=20)
    thumb = models.ImageField(upload_to='thumbs/')
    content = models.TextField()
    created_at = models.DateField(default=timezone.now)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_list_detail', kwargs={'post_list_id': self.id})

class PostListPics(models.Model):
    post_list = models.ForeignKey(
        'PostList', on_delete=models.CASCADE, related_name='pics'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField(null=True, blank=True)
    # ① 원본
    image = models.ImageField(upload_to='post_list_pics/original/')

    # ② 썸네일: 일반 ImageField 로 선언
    thumbnail = models.ImageField(
        upload_to='post_list_pics/thumbnails/',
        blank=True, editable=False
    )

    # ① EXIF 정보를 JSON 형태로 저장할 필드
    metadata = models.JSONField(
        blank=True, null=True,
        help_text="EXIF 메타데이터(카메라, 렌즈, ISO 등)를 저장"
    )

    def _parse_exif_value(self, value):
        # IFDRational → (numerator, denominator)
        if isinstance(value, IFDRational):
            return (value.numerator, value.denominator)
        # bytes → 문자열
        if isinstance(value, (bytes, bytearray)):
            try:
                return value.decode(errors='ignore')
            except:
                return str(value)
        # 리스트·튜플은 재귀 처리
        if isinstance(value, (list, tuple)):
            return [self._parse_exif_value(v) for v in value]
        return value

    def save(self, *args, **kwargs):
        # 1 원본 저장
        super().save(*args, **kwargs)

        # 2 thumbnail이 비어 있으면 생성
        if self.image and not self.thumbnail:
            # 원본 파일 열기
            img = Image.open(self.image.path)
            # 비율 유지하며 썸네일 크기 지정 (예: 최대 200×200)
            img.thumbnail((200, 9999), Image.LANCZOS)

            # 메모리 버퍼에 JPEG로 저장
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=70)

            # 원본 파일명 가져오기
            base_name = os.path.basename(self.image.name)
            # 썸네일 필드에 저장 (물리 파일 생성)
            self.thumbnail.save(
                base_name,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            # thumbnail 필드만 업데이트
            super().save(update_fields=['thumbnail'])

        # 2) EXIF 추출 및 JSON 변환
        if self.image and not self.metadata:
            try:
                img = Image.open(self.image.path)
                raw_exif = img._getexif() or {}
                exif = {}
                for tag_id, val in raw_exif.items():
                    name = ExifTags.TAGS.get(tag_id, tag_id)
                    exif[name] = self._parse_exif_value(val)

                # 필요한 키만 걸러내기
                wanted = [
                    'Make','Model','LensModel',
                    'FNumber','ExposureTime','ISOSpeedRatings',
                    'FocalLength','DateTimeOriginal'
                ]
                filtered = {k: exif[k] for k in wanted if k in exif}

                self.metadata = filtered
                super().save(update_fields=['metadata'])
            except Exception as e:
                # EXIF 파싱 실패 시 로깅
                print("EXIF parsing error:", e)

    def __str__(self):
        return f'Image for {self.post_list.title}'

class Post(models.Model):
    title = models.CharField(max_length=100)
    place = models.CharField(max_length=50, null=True, blank=True)
    place_link = models.URLField(validators=[validate_place_link], blank=True)
    content = CKEditor5Field(config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
