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

    profile_pic = models.ImageField(default='default_profile_pic.jpg', upload_to='profile_pics')

    intro = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # --- 썸네일 생성 로직 시작 ---
        # (1) 인스턴스가 기존에 DB에 있던 것이라면, old_pic 참조
        old_pic = None
        if self.pk:
            try:
                old = User.objects.get(pk=self.pk)
                old_pic = old.profile_pic
            except User.DoesNotExist:
                pass

        # (2) 새로 업로드된 파일이 있으면 thumbnail 생성
        if self.profile_pic and (not old_pic or old_pic.name != self.profile_pic.name):
            # 메모리에서 이미지 열기
            img = Image.open(self.profile_pic)
            # 비율 유지 최대 너비 300px
            img.thumbnail((200, 200), Image.LANCZOS)

            # JPEG로 메모리에 저장
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=80)

            # 원본 파일명에서 확장자 따오기
            base, ext = os.path.splitext(os.path.basename(self.profile_pic.name))
            thumb_name = f'{base}{ext}'

            # profile_pic 필드 덮어쓰기 (메모리 내용으로)
            self.profile_pic.save(
                thumb_name,
                ContentFile(thumb_io.getvalue()),
                save=False
            )

            # (3) 이전 파일이 남아 있다면 파일 시스템에서 삭제
            if old_pic and old_pic.name != self.profile_pic.name:
                old_pic.delete(save=False)
        # --- 썸네일 생성 로직 끝 ---

        super().save(*args, **kwargs)

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
    
    def save(self, *args, **kwargs):
        # 1) 사용자가 올린 이미지를 self.thumb.file 에서 바로 읽어들임
        uploaded_file = self.thumb

        if uploaded_file:
            # 메모리에서 이미지 열기
            img = Image.open(uploaded_file)
            # 썸네일 비율 유지, 너비 200px
            img.thumbnail((200, 9999), Image.LANCZOS)

            # 메모리 버퍼에 JPEG로 저장
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=70)

            # 원래 파일명을 유지
            base_name = os.path.basename(uploaded_file.name)

            # self.thumb 파일 객체를 덮어씀
            self.thumb.save(
                base_name,
                ContentFile(thumb_io.getvalue()),
                save=False  # 아직 DB 반영하지 않음
            )

        # 2) 최종적으로 DB에 한 번만 저장
        super().save(*args, **kwargs)

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
        # 1) 원본 저장 (update든 create든)
        super().save(*args, **kwargs)

        # 2) 항상 썸네일 재생성
        if self.image:
            img = Image.open(self.image.path)
            img.thumbnail((200, 9999), Image.LANCZOS)

            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=70)

            base, ext = os.path.splitext(os.path.basename(self.image.name))
            thumb_name = f"{base}{ext}"

            # 덮어쓰기
            self.thumbnail.save(
                thumb_name,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
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
