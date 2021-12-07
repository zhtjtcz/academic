import os

from django import forms
from django.shortcuts import render

from academic.settings import MEDIA_ROOT
from message.models import Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from user.views import *
from datetime import datetime
from message.models import *
from paper.models import *


# Create your views here.

def create_message(type, uid, pid, title, content=''):
    message = Message()
    message.uid = uid
    message.pid = pid
    message.type = type
    message.title = title
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


@csrf_exempt
def feedback(request):
    if request.method == 'POST':
        id = check_session(request)
        if id == 0:
            return JsonResponse({'result': ERROR, 'message': r'请先登录'})
        data_json = json.loads(request.body)
        content = data_json.get('content', '')
        create_message(FEEDBACK, id, 0, data_json.get('title', ''), content)
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
        messages.append({
            'id': x.id,
            'paper': x.title,
            'username': user.username,
            'isdeal': x.isdeal,
            'date': str(x.date)[:19],
            'uid': x.uid,
            'pid': x.pid,
            'content': x.content
        	}
        )
        if x.type == CLAIM_PAPER:
            messages[-1]['realname'] = Scholar.objects.get(uid=x.uid).realname
    messages.sort(key=lambda x: -x["id"])
    return JsonResponse({'result': ACCEPT, 'message': '获取成功！', 'messages': messages})


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
    message = Message.objects.get(id=id)
    if message.isdeal == True:
        return JsonResponse({'result': ACCEPT, 'message': r'已完成处理！'})
    message.isdeal = True
    message.isread = True
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
		data_json = json.loads(request.body)
		uid = int(data_json['uid'])
		create_message(APPEAL_IDENTITY, uid, 0, data_json.get('title', ''), data_json.get('content', ''))
		return JsonResponse({'result': ACCEPT, 'message': r'举报成功！'})

@csrf_exempt
def appeal_paper(request):
	if request.method == 'POST':
		id = check_session(request)
		if id == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		data_json = json.loads(request.body)
		uid = int(data_json['uid'])
		pid = int(data_json['pid'])
		create_message(APPEAL_PAPER, uid, pid, data_json.get('title', ''))
		return JsonResponse({'result': ACCEPT, 'message': r'举报成功！'})


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'????'})
    file = request.FILES.get('file', None)
    if not file:
        return JsonResponse({'result': ERROR, 'message': r'上传失败！'})
    destination = open(os.path.join(MEDIA_ROOT, file.name), 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    return JsonResponse({'result': ACCEPT, 'message': r'上传成功! '})