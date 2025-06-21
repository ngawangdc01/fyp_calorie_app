from django.db import models
from django.conf import settings
from datetime import date

class Activity(models.Model):
    """
    Stores predefined physical activities.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    duration = models.FloatField()  # in minutes
    weight_kg = models.FloatField(default=0.0)  # captured at time of logging
    calories_burned = models.FloatField()
    logged_date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity.name} ({self.duration} min)"