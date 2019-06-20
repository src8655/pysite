from django.db import models


# Create your models here.
class Guestbook(models.Model):
    name = models.CharField(max_length=10)
    password = models.CharField(max_length=10)
    content = models.TextField()
    regdate = models.DateField(auto_now=True)
