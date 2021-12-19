from django.db import models


# Create your models here.
class Message(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=100, blank=True, null=True)
	type = models.IntegerField()
	uid = models.IntegerField(default=0)
	pid = models.IntegerField(null=True, blank=True, default = 0)
	isread = models.BooleanField(default = False)
	isdeal = models.IntegerField(null = True, blank = True, default = 0)
	date = models.CharField(max_length=50, blank=True, null=True)
	content = models.TextField(null=True, blank=True, default = "")
	contact= models.CharField(max_length=50, blank=True, null=True)
	reply = models.TextField(null=True, blank=True)
	url = models.CharField(max_length=50, default='')


class Feedback(models.Model):
	id = models.AutoField(primary_key=True)
	uid = models.IntegerField()
	mid = models.IntegerField()
	type = models.IntegerField(default = 1)
	reply = models.TextField(null=True, blank=True)
	isdeal = models.BooleanField(default = False)
	date = models.CharField(max_length=50, blank=True, null=True)
	url =  models.CharField(max_length=50, default='default_profile.png')
