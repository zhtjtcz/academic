from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from captcha.models import CaptchaStore
from academic.values import *
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
# Create your views here.
from user.models import *
import json

'''
@swagger_auto_schema(method='post',
                     tags=['用户登录注册相关'],
                     operation_summary='登录',
                     responses={200: '登录成功', 401: '用户重复登录', 402: '用户名不存在', 403: '密码错误', 404: '用户未经过邮箱确认', 405: '表单格式错误，即用户名或密码不符合规则'},
                     manual_parameters=['A', 'B']
                     )
@api_view(['POST'])
'''
@csrf_exempt
def test(request):
	if request.method == 'POST':
		return JsonResponse({'result': ACCEPT, 'message': r'POST!'})
	else:
		return JsonResponse({'result': ACCEPT, 'message': r'GET!'})

@csrf_exempt
def set_introduction(request):
	if request.method == 'POST':
		# TODO check session
		data_json = json.loads(request.body)
		uid = int(data_json['uid'])
		introduction_html = data_json['introduction_html']
		introduction_md = data_json['introduction_md']
		scholar = Scholar.objects.get(uid = uid)
		scholar.introduction = introduction_md + MAGIC + introduction_html
		scholar.save()
		return JsonResponse({'result': ACCEPT, 'message': r'修改成功!'})

@csrf_exempt
def get_introduction(request):
	if request.method == 'POST':
		# TODO check session
		data_json = json.loads(request.body)
		uid = int(data_json['uid'])
		scholar = Scholar.objects.get(uid = uid)
		intro = scholar.introduction
		if intro == None:
			intro_md = INTO_TEMPLATE_MD
			intro_html = INTO_TEMPLATE_HTML
		else:
			intro_md,intro_html = intro.split(MAGIC)
		return JsonResponse({'result': ACCEPT, 'message': r'获取成功!', 'introduction_md':intro_md, 'introduction_html':intro_html})