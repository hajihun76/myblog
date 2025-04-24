from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class BusQueryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    bus_number = models.IntegerField()
    queried_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.bus_number}"

class BusOrderLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    bus_number = models.CharField(max_length=10)
    queue_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_access_busorder", "Can access bus order feature"),
            ("can_access_all_logs", "Can view all user logs"),  # ✅ 관리자용
        ]

    def __str__(self):
        return f"{self.date} - {self.bus_number} - {self.queue_number}"