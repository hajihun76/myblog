from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BusQueryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    bus_number = models.IntegerField()
    queried_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.bus_number}"
