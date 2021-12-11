from django.db import models


# Create your models here.

class Paper(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=100)
	keyword = models.TextField(null=True, blank=True)
	abstract = models.TextField(null=True, blank=True)
	venue = models.CharField(max_length=100, null=True, blank=True)
	year = models.IntegerField(default=-1)
	cite = models.IntegerField(default=-1)
	url = models.TextField(null=True, blank=True)
	lang = models.CharField(max_length=20, null=True, blank=True)
	doi = models.CharField(max_length=50, null=True, blank=True)
	field = models.TextField(null=True, blank=True)
	download = models.IntegerField(default=0)


class AuthorInfo(models.Model):
	pid = models.IntegerField()
	author = models.CharField(max_length=50)
	rank = models.IntegerField()


class Claim(models.Model):
	uid = models.IntegerField()
	pid = models.IntegerField()


class Favor(models.Model):
	uid = models.IntegerField()
	pid = models.IntegerField()

	def to_dic(self):
		return {'uid': self.uid, 'pid': self.pid}

class Comment(models.Model):
	id = models.AutoField(primary_key=True)
	pid = models.IntegerField()
	uid = models.IntegerField()
	time = models.CharField(max_length = 50)
	comment = models.TextField(null=True, blank=True)
	reply = models.IntegerField()
	replyuid = models.IntegerField(null=True, blank=True, default=0)
	replyname = models.CharField(max_length = 50, null=True, blank=True, default='')


class Relation(models.Model):
    name1 = models.CharField(max_length=50, default='')
    name2 = models.CharField(max_length=50, default='')
    times = models.IntegerField()
