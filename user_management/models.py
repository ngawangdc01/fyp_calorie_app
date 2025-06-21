from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.conf import settings
from datetime import date
from django.utils import timezone

class Status(models.Model):
    """
    Stores weight status categories for each range of BMI.
    """
    category = models.CharField(max_length=20, unique=True)
    min_bmi = models.FloatField()
    max_bmi = models.FloatField()

    def __str__(self):
        return self.category

class CustomUserManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("You must provide a username")
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)
    
    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Stores user authentication credentials and personal metrics.
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Django handles encryption

    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female")]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height = models.FloatField()
    weight = models.FloatField()
    bmi = models.FloatField(editable=False)

    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)

    is_visible_in_leaderboard = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['gender', 'height', 'weight']

    def update_bmi(self):
        """Automatically updates BMI based on height and weight."""
        if self.height > 0:
            self.bmi = round(self.weight / (self.height ** 2), 2)
            self._assign_status()

    def _assign_status(self):
        """Assigns a BMI status based on predefined BMI categories."""
        status = Status.objects.filter(min_bmi__lte=self.bmi, max_bmi__gte=self.bmi).first()
        if status and self.status != status:
            self.status = status

    def save(self, *args, **kwargs):
        """Ensure BMI and status are updated only when needed, avoiding infinite recursion."""
        if not kwargs.pop("skip_update", False):
            self.update_bmi()
        super().save(*args, **kwargs)

class WeightHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weight_kg = models.FloatField()
    recorded_at = models.DateField()

    class Meta:
        unique_together = ('user', 'recorded_at')
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.user.username} - {self.weight_kg} kg on {self.recorded_at}"