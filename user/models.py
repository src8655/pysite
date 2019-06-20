from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=32)
    gender = models.CharField(max_length=10)
    joindate = models.DateField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(self.name, self.email, self.gender, self.joindate)