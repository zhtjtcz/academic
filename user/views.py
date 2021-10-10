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