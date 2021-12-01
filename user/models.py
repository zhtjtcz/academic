from django.db import models


# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    scholar = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)


class Scholar(models.Model):
    uid = models.IntegerField()
    realname = models.CharField(max_length=50)
    belong = models.CharField(max_length=50, null=True, blank=True)
    interest = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    download = models.IntegerField(default=0)
    cite = models.IntegerField(default=0)
