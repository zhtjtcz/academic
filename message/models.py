from django.db import models


# Create your models here.
class Message(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=100, blank=True, null=True)
	type = models.IntegerField()
	uid = models.IntegerField()
	pid = models.IntegerField(null=True, blank=True, default = 0)
	isread = models.BooleanField(default = False)
	isdeal = models.IntegerField(null = True, blank = True, default = 0)
	date = models.DateField()
	content = models.TextField(null=True, blank=True, default = "")
