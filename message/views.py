import os
import random
import time
import uuid

from django import forms
from django.shortcuts import render

from academic.settings import MEDIA_ROOT
from message.models import Message
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from user.models import *
import json
from academic.tools import check_session
from datetime import datetime
from message.models import *
from paper.models import *


# Create your views here.

def create_message(type, uid, pid, title, content='', url='', contact=''):
	message = Message()
	message.uid = uid
	message.pid = pid
	message.type = type
	message.title = title
	message.url = url
	message.contact = contact
	message.date = datetime.now()
	user = User.objects.get(id=uid)

	if type == CLAIM_PAPER:
		paper = Paper.objects.get(id=pid)
		content = "用户 %s 申请认领文章 %s , 请及时处理" % (user.username, paper.title)
		message.content = content
	elif type == APPEAL_IDENTITY:
		message.content = content
	elif type == APPEAL_PAPER:
		paper = Paper.objects.get(id=pid)
		message.content = content
	elif type == FEEDBACK:
		message.content = content
	else:
		print("Fuck Frontend")
	message.save()
	rid = message.id
	
	feedback = Feedback()
	feedback.date = datetime.now()
	feedback.uid = uid
	feedback.mid = message.id
	feedback.type = type
	feedback.reply = '您的申诉已提交，请等待管理员处理'	if type in [APPEAL_IDENTITY, APPEAL_PAPER] else '您的反馈已提交，请等待管理员处理'
	feedback.save()
	return rid

@csrf_exempt
def feedback(request):
	if request.method == 'POST':
		id = check_session(request)
		if id == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		# data_json = json.loads(request.body)
		data_json = request.POST
		content = data_json.get('content', '')
		contact = data_json.get('contact', '')
		file = request.FILES.get('file', None)
		filename = ''
		if file:
			_, type = os.path.splitext(file.name)
			if type != '.jpg' and type != '.png':
				return JsonResponse({'result': ERROR, 'message': r'请上传JPG或PNG格式图片！'})
			filename = "m" + str(id) + "_" + str(uuid.uuid1()) + type
			with open(os.path.join(MEDIA_ROOT, filename).replace('\\', '/'), "wb") as destination:
				for chunk in file.chunks():
					destination.write(chunk)
		create_message(FEEDBACK, id, 0, data_json.get('title', ''), content, filename, contact)
		return JsonResponse({'result': ACCEPT, 'message': r'反馈成功！'})


@csrf_exempt
def get_messages(request):
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	type = int(data_json['type'])
	origin = [x for x in Message.objects.filter(type=type)]
	messages = []
	for x in origin:
		user = User.objects.get(id=x.uid)
		realname = ''
		if x.type == APPEAL_IDENTITY:
			realname = Scholar.objects.get(uid=x.uid).realname
		messages.append({
			'id': x.id,
			'paper': x.title,
			'username': user.username,
			'isdeal': x.isdeal,
			'date': str(x.date)[:19],
			'uid': x.uid,
			'pid': x.pid,
			'content': x.content,
			'realname': realname,
			'contact': x.contact,
			'url': x.url,
			}
		)
		if x.type == CLAIM_PAPER:
			messages[-1]['realname'] = Scholar.objects.get(uid=x.uid).realname
	messages.sort(key=lambda x: -x["id"])
	return JsonResponse({'result': ACCEPT, 'message': '获取成功！', 'messages': messages})

@csrf_exempt
def get_feedbacks(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	origin = [x for x in Feedback.objects.filter(uid = id)]
	feedbacks = []
	for x in origin:
		feedbacks.append({
			'id': x.id,
			'type': x.type,
			'reply': x.reply,
			'isdeal': x.isdeal,
			'date': str(x.date)[:19],
			'url': x.url,
		})
	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'feedbacks': feedbacks})

@csrf_exempt
def get_message(request):
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	message = Message.objects.get(id=id)
	message.isread = True
	message.save()

	out = {
		'type': message.type,
		'paper': message.title,
		'uid': message.uid,
		'pid': message.pid,
		'isread': message.isread,
		'isdeal': message.isdeal,
		'date': str(message.date)[:19],
		'content': message.content
	}
	return JsonResponse({'result': ACCEPT, 'message': out})

@csrf_exempt
def reply(request):
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	user = User.objects.get(id=id)
	if user.admin == False:
		return JsonResponse({'result': ERROR, 'message': r'没有权限！'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	reply = data_json['reply']


	message = Message.objects.get(id = id)
	message.isdeal = True

	message.save()
	# Update the message

	feedback = Feedback.objects.get(mid = id)
	feedback.isdeal = True
	feedback.reply = reply
	feedback.save()
	# Update the feedback

	return JsonResponse({'result': ACCEPT, 'message': r'反馈成功！'})

@csrf_exempt
def deal_message(request):
    if request.method != 'POST':
        return
    id = check_session(request)
    if id == 0:
        return JsonResponse({'result': ERROR, 'message': r'请先登录'})



@csrf_exempt
def deal_claim(request):
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	user = User.objects.get(id=id)
	if user.admin == False:
		return JsonResponse({'result': ERROR, 'message': r'没有权限！'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	result = int(data_json['result'])
	# content = int(data_json.get('content', ''))  # 新添加的，optional
	message = Message.objects.get(id=id)
	if message.isdeal != 0:
		return JsonResponse({'result': ACCEPT, 'message': r'已完成处理！'})
	message.isdeal = result
	message.isread = True
	# message.content = content  # 新添加
	message.save()
	if result == 1:
		if Claim.objects.filter(uid=message.uid, pid=message.pid).exists() == False:
			claim = Claim(uid=message.uid, pid=message.pid)
			claim.save()
			user = User.objects.get(id=message.uid)
			user.scholar = True
			user.save()
			paper = Paper.objects.get(id=message.pid)
			scholar = Scholar.objects.get(uid=message.uid)
			scholar.cite += paper.cite
			scholar.save()

	return JsonResponse({'result': ACCEPT, 'message': r'处理完毕！'})

@csrf_exempt
def appeal_user(request):
	if request.method == 'POST':
		id = check_session(request)
		if id == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		# data_json = json.loads(request.body)
		data_json = request.POST
		# uid = int(data_json['uid'])
		uid = data_json.get('uid', 0)
		file = request.FILES.get('file', None)
		filename = ''
		if file:
			_, type = os.path.splitext(file.name)
			if type != '.jpg' and type != '.png':
				return JsonResponse({'result': ERROR, 'message': r'请上传JPG或PNG格式图片！'})
			filename = "m" + str(id) + "_" + str(uuid.uuid1()) + type
			with open(os.path.join(MEDIA_ROOT, filename).replace('\\', '/'), "wb") as destination:
				for chunk in file.chunks():
					destination.write(chunk)
		contact = data_json.get('contact', '')
		create_message(APPEAL_IDENTITY, uid, 0, data_json.get('title', ''), data_json.get('content', ''), filename, contact)
		return JsonResponse({'result': ACCEPT, 'message': r'举报成功！'})

@csrf_exempt
def appeal_paper(request):
	if request.method == 'POST':
		id = check_session(request)
		if id == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		# data_json = json.loads(request.body)
		data_json = request.POST
		# uid = int(data_json['uid'])
		uid = data_json.get('uid', 0)
		pid = int(data_json['pid'])
		file = request.FILES.get('file', None)
		filename = ''
		if file:
			_, type = os.path.splitext(file.name)
			if type != '.jpg' and type != '.png':
				return JsonResponse({'result': ERROR, 'message': r'请上传JPG或PNG格式图片！'})
			filename = "m" + str(id) + "_" + str(uuid.uuid1()) + type
			with open(os.path.join(MEDIA_ROOT, filename).replace('\\', '/'), "wb") as destination:
				for chunk in file.chunks():
					destination.write(chunk)
		contact = data_json.get('contact', '')
		create_message(APPEAL_PAPER, uid, pid, data_json.get('title', ''), filename, contact)
		return JsonResponse({'result': ACCEPT, 'message': r'举报成功！'})


class UploadFileForm(forms.Form):
	title = forms.CharField(max_length=50)
	file = forms.FileField()


@csrf_exempt
def upload_file(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'????'})
	file = request.FILES.get('file', None)
	name = request.POST.get('name')
	if not file:
		return JsonResponse({'result': ERROR, 'message': r'上传失败！'})
	with open(os.path.join(MEDIA_ROOT, name).replace('\\', '/'), 'wb') as destination:
		for chunk in file.chunks():
			destination.write(chunk)
	return JsonResponse({'result': ACCEPT, 'message': r'上传成功! '})

@csrf_exempt
def download_file(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'????'})


@csrf_exempt
def look_feedback_img(request):
	if request.method == 'POST':
		return JsonResponse({'result': ERROR, 'message': r'????'})
	data = request.GET
	file_name = data.get("file_name")
	imagepath = os.path.join(MEDIA_ROOT, file_name).replace('\\', '/')  # 图片路径
	try:
		# with open(imagepath, 'rb') as f:
		f = open(imagepath, 'rb')
		image_data = f.read()
		return HttpResponse(image_data, content_type="image/" + file_name[-3:])
	except Exception as e:
		imagepath = os.path.join(MEDIA_ROOT, 'default_profile.png').replace('\\', '/')  # 图片路径
		with open(imagepath, 'rb') as f:
			image_data = f.read()
		return HttpResponse(image_data, content_type="image/png")

