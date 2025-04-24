# busorder/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_busorder_permission(sender, **kwargs):
    if sender.name != 'busorder':
        return

    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    content_type, _ = ContentType.objects.get_or_create(app_label='busorder', model='dummy_model')

    Permission.objects.get_or_create(
        codename='can_access_busorder',
        name='Can Access Bus Order Feature',
        content_type=content_type,
    )

    Permission.objects.get_or_create(
        codename='can_view_all_logs',
        name='Can View All Bus Order Logs',
        content_type=content_type,
    )
