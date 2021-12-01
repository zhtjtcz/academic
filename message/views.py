from django.shortcuts import render
from message.models import Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from user.views import *
from datetime import datetime
from message.models import *
from paper.models import *
# Create your views here.

def create_message(type, uid, pid):
	message = Message()
	message.uid = uid
	message.pid = pid
	message.type = type
	message.date = datetime.now()
	user = User.objects.get(id = uid)
	paper = Paper.objects.get(id = pid)
	if type == CLAIM_PAPER:
		content = "用户 %s 申请认领文章 %s , 请及时处理"%(user.username, paper.title)
		message.content = content
		message.save()
	else:
		pass
		# TODO add more type

@csrf_exempt
def get_messages(request):
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	type = int(data_json['type'])
	origin = [x for x in Message.objects.filter(type = type)]
	messages = []
	for x in origin:
		messages.append({
			"id": x.id,
			"isdeal": x.isdeal,
			"isread": x.isread,
			"date": str(x.date)[:19]
		}
	)
	messages.sort(key = lambda x: -x["id"])
	return JsonResponse({'result': ACCEPT, 'message': '获取成功！', 'messages': messages})	

@csrf_exempt
def get_message(request):
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	message = Message.objects.get(id = id)
	message.isread = True
	message.save()

	out = {
		'type': message.type,
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
	user = User.objects.get(id = id)
	if user.admin == False:
		return JsonResponse({'result': ERROR, 'message': r'没有权限！'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	result = int(data_json['result'])
	message = Message.objects.get(id = id)
	if message.isdeal == True:
		return JsonResponse({'result': ACCEPT, 'message': r'已完成处理！'})
	message.isdeal = True
	message.isread = True
	message.save()
	if result == 1:
		if Claim.objects.filter(uid = message.uid, pid = message.pid).exists() == False:
			claim = Claim(uid = message.uid, pid = message.pid)
			claim.save()
	return JsonResponse({'result': ACCEPT, 'message': r'处理完毕！'})
