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
from hashlib import md5
import re

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
def login(request):
    if request.method == 'POST':
        # if request.session.get('is_login') is not True:
        #     return JsonResponse({'result': ERROR, 'message': r'已登录!'})
        data_json = json.loads(request.body)
        username = data_json['username']
        password = data_json['password']
        if not User.objects.filter(username=username).exists():
            return JsonResponse({'result': ERROR, 'message': r'用户名不存在'})
        user = User.objects.get(username=username)
        password = password[:1] + SALT1 + password[1:2] + SALT2 + password[2:-2] + SALT3 + password[-2:-1] + SALT4 + \
                   password[-1:]
        password = md5(password.encode("utf8")).hexdigest()
        if password != user.password:
            return JsonResponse({'result': ERROR, 'message': r'密码错误'})
        request.session['is_login'] = True
        request.session['user'] = user.id
        return JsonResponse({'result': ACCEPT, 'message': r'登录成功!', 'scholar': user.scholar, 'admin': user.admin})


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        username = data_json['username']
        password = data_json['password']
        check_password = data_json['check_password']
        email = data_json['email']
        if User.objects.filter(username=username).exists():
            return JsonResponse({'result': ERROR, 'message': r'用户名已存在'})
        if not 1 <= len(str(username)) <= 32:
            return JsonResponse({'result': ERROR, 'message': r'用户名格式不正确'})
        if not re.match('^((?=.*[0-9].*)(?=.*[A-Z].*)|(?=.*[0-9].*)(?=.*[a-z].*)|(?=.*[a-z].*)(?=.*[A-Z].*)).{6,16}$',
                        password):
            return JsonResponse({'result': ERROR, 'message': r'密码不合法'})
        if password != check_password:
            return JsonResponse({'result': ERROR, 'message': r'两次密码不一致'})
        password = password[:1] + SALT1 + password[1:2] + SALT2 + password[2:-2] + SALT3 + password[-2:-1] + SALT4 + \
                   password[-1:]
        password = md5(password.encode("utf8")).hexdigest()
        user = User(username=username, password=password, email=email)
        user.save()
        return JsonResponse({'result': ACCEPT, 'message': r'注册成功'})


@csrf_exempt
def set_introduction(request):
    if request.method == 'POST':
        # if request.session.get('is_login') is not True:
        #     return JsonResponse({'result': ERROR, 'message': r'请先登录'})
        data_json = json.loads(request.body)
        # uid = request.session['user']
        uid = 1
        introduction_html = data_json['introduction_html']
        introduction_md = data_json['introduction_md']
        scholar = Scholar.objects.get(uid=uid)
        scholar.introduction = introduction_md + MAGIC + introduction_html
        scholar.save()
        return JsonResponse({'result': ACCEPT, 'message': r'修改成功!'})


@csrf_exempt
def get_introduction(request):
    if request.method == 'POST':
        # if request.session.get('is_login') is not True:
        #     return JsonResponse({'result': ERROR, 'message': r'请先登录'})
        # uid = request.session['user']
        uid = 1
        scholar = Scholar.objects.get(uid=uid)
        intro = scholar.introduction
        if intro is None:
            intro_md = INTO_TEMPLATE_MD
            intro_html = INTO_TEMPLATE_HTML
        else:
            intro_md, intro_html = intro.split(MAGIC)
        return JsonResponse(
            {'result': ACCEPT, 'message': r'获取成功!', 'introduction_md': intro_md, 'introduction_html': intro_html})


@csrf_exempt
def set_scholar_info(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
    # if request.session.get('is_login') is not True:
    #     return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    # id = request.session['user']
    id = 1
    info = User.objects.get(id=id)
    if not info.scholar:
        return JsonResponse({'result': ACCEPT, 'message': r'您还没有认证!'})
    data_json = json.loads(request.body)
    scholar = Scholar.objects.get(uid=id)
    scholar.realname = data_json['realname']
    scholar.website = data_json['website']
    scholar.interest = data_json['interest']
    scholar.belong = data_json['belong']
    scholar.save()
    return JsonResponse(
        {'result': ACCEPT, 'message': r'修改成功!'})


@csrf_exempt
def get_scholar_info(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
    # if request.session.get('is_login') is not True:
    #     return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    # id = request.session['user']
    id = 1
    info = User.objects.get(id=id)
    if not info.scholar:
        return JsonResponse({'result': ACCEPT, 'message': r'您还没有认证!'})
    scholar = Scholar.objects.get(uid=info.id)
    return JsonResponse(
        {'result': ACCEPT, 'message': r'获取成功!', 'realname': scholar.realname, 'website': scholar.website,
         'interest': scholar.interest, 'belong': scholar.belong, 'download': scholar.download, 'cite':scholar.cite})


@csrf_exempt
def logout(request):
    if request.session.get('is_login'):
        request.session.flush()
        return JsonResponse({'result': ACCEPT, 'message': r'已登出!'})
    else:
        return JsonResponse({'result': ERROR, 'message': r'请先登录!'})
