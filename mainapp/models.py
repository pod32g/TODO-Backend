from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Todo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    content = models.TextField()
    timestamp = models.DateField(auto_now=True)
    status = models.CharField(max_length=20)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
