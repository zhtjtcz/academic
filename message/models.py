from django.db import models


# Create your models here.
class Message(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.IntegerField()
	uid = models.IntegerField()
	pid = models.IntegerField(null=True, blank=True, default = 0)
	isread = models.BooleanField(default = False)
	date = models.DateField()
	content = models.TextField(null=True, blank=True, default = "")
