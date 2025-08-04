from django.db import models
from django.contrib.auth.models import User

class StressPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_images/')
    stress_level = models.CharField(max_length=10)
    mood = models.CharField(max_length=10)
    stress_type = models.CharField(max_length=20)
    confidence = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
