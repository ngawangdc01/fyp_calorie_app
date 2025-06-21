from django.db import models
from django.conf import settings  # ✅ important for custom user model

def was_edited(self):
    return self.updated_at > self.created_at

class Discussion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='discussion_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def was_edited(self):
        return self.updated_at > self.created_at

    def __str__(self):
        return self.title

class Reply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='reply_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def was_edited(self):
        return self.updated_at > self.created_at

    def __str__(self):
        return f"Reply by {self.user.username}"
