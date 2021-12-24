import os
import random
import time
import uuid

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from captcha.models import CaptchaStore
from academic.settings import MEDIA_ROOT
from academic.values import *
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
# Create your views here.
from user.models import *
from paper.models import *
from academic.tools import check_session
from paper.views import get_papers
import json
from hashlib import md5
import re
from academic.settings import Redis
import difflib
from message.models import *
from datetime import datetime

@csrf_exempt
def test(request):
    if request.method == 'POST':
        return JsonResponse({'result': ACCEPT, 'message': r'POST!'})
    else:
        return JsonResponse({'result': ACCEPT, 'message': r'GET!'})

@csrf_exempt
def islogin(request):
	if check_session(request) != 0:
		user = User.objects.get(id = check_session(request))
		return JsonResponse({'result': ACCEPT, 'scholar': user.scholar, 'admin': user.admin,
				'id':user.id, 'username': user.username})
	else:
		return JsonResponse({'result': ERROR})

@csrf_exempt
def login(request):
    if request.method == 'POST':
        #id = check_session(request)
        #if id > 0:
        #    return JsonResponse({'result': ERROR, 'message': r'已登录!'})
        if request.session.get('user', 0) != 0:
            return JsonResponse({'result': ERROR, 'message': r'已登录!'})
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
        return JsonResponse({'result': ACCEPT, 'message': r'登录成功!', 'scholar': user.scholar, 'admin': user.admin, 'id': user.id})


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        username = data_json['username']
        password = data_json['password']
        check_password = data_json['check_password']
        email = data_json.get('email', '')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'result': ERROR, 'message': r'用户名已存在'})
        if not 1 <= len(str(username)) <= 32:
            return JsonResponse({'result': ERROR, 'message': r'用户名格式不正确'})
        if not re.match('^((?=.*[0-9].*)(?=.*[A-Z].*)|(?=.*[0-9].*)(?=.*[a-z].*)|(?=.*[a-z].*)(?=.*[A-Z].*)).{6,16}$',
                        password):
            return JsonResponse({'result': ERROR, 'message': r'密码必须包含大写字母、小写字母、数字中的至少两种，且长度要在6到16之间！'})
        if password != check_password:
            return JsonResponse({'result': ERROR, 'message': r'两次密码不一致'})
        password = password[:1] + SALT1 + password[1:2] + SALT2 + password[2:-2] + SALT3 + password[-2:-1] + SALT4 + \
                   password[-1:]
        password = md5(password.encode("utf8")).hexdigest()
        user = User(username=username, password=password, email=email)
        user.save()
        return JsonResponse({'result': ACCEPT, 'message': r'注册成功'})

@csrf_exempt
def jump(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	name = data_json['name']
	if Claim.objects.filter(pid = id).exists() == False:
		return JsonResponse({'result': ERROR, 'message':r'查无此人'})
	claims = Claim.objects.filter(pid = id)
	for x in claims:
		scholar = Scholar.objects.get(uid = x.uid)
		r = difflib.SequenceMatcher(lambda x:x == " ", name, scholar.realname).ratio()
		if r >= 0.8:
			return JsonResponse({'result': ACCEPT, 'message':r'获取成功', 'id': scholar.uid})
	return JsonResponse({'result': ERROR, 'message':r'查无此人'})


@csrf_exempt
def get_scholar_id(request):
	data_json = json.loads(request.body)
	name = data_json.get('name', '')
	if len(name) > 0:
		if Scholar.objects.filter(realname__icontains = name).exists() == False:
			return JsonResponse({'result': ACCEPT, 'id': -1, 'isself': False})
		scholar = Scholar.objects.get(realname__icontains = name)
		id = check_session(request)
		return JsonResponse({'result': ACCEPT, 'id': scholar.uid, 'isself': scholar.uid == id})
	else:
		id = int(data_json['id'])
		scholar = Scholar.objects.get(uid = id)
		login_id = check_session(request)
		return JsonResponse({'result': ACCEPT, 'name': scholar.realname, 'isself': login_id == id})

@csrf_exempt
def set_introduction(request):
    if request.method == 'POST':
        if request.session.get('is_login') is not True:
            return JsonResponse({'result': ERROR, 'message': r'请先登录'})
        data_json = json.loads(request.body)
        uid = request.session['user']
        introduction_html = data_json['introduction_html']
        introduction_md = data_json['introduction_md']
        scholar = Scholar.objects.get(uid=uid)
        scholar.introduction = introduction_md + MAGIC + introduction_html
        scholar.save()
        return JsonResponse({'result': ACCEPT, 'message': r'修改成功!'})


@csrf_exempt
def get_introduction(request):
    if request.method == 'POST':
        if check_session(request) == 0:
            return JsonResponse({'result': ERROR, 'message': r'请先登录'})
        data_json = json.loads(request.body)
        uid = int(data_json.get('id', request.session['user']))
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
    id = check_session(request)
    if id == 0:
        return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    info = User.objects.get(id=id)
    if not info.scholar:
        return JsonResponse({'result': ACCEPT, 'message': r'您还没有认证!'})
    data_json = json.loads(request.body)
    scholar = Scholar.objects.get(uid=id)
    # scholar.realname = data_json['realname']
    scholar.website = data_json['website']
    scholar.interest = data_json['interest']
    scholar.belong = data_json['belong']
    scholar.save()
    return JsonResponse({'result': ACCEPT, 'message': r'修改成功!'})


@csrf_exempt
def get_scholar_info(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
	
	data_json = json.loads(request.body)
	id = int(data_json.get('id', 0))
	author = data_json.get('author', '')
	
	if len(author) == 0:
		if Scholar.objects.filter(uid = id).exists() == False:
			return JsonResponse({'result': ERROR, 'message': '还未认证!'})
		scholar = Scholar.objects.get(uid = id)
	else:
		if Scholar.objects.filter(realname__icontains = author).exists() == False:
			return JsonResponse({'result': ERROR, 'message': '还未认证!'})
		scholar = Scholar.objects.get(realname__icontains = author)
	
	papers = []
	if Claim.objects.filter(uid = scholar.uid).exists() == True:
		origin = [x for x in Claim.objects.filter(uid = scholar.uid)]
		papers = get_papers(origin)
	
	Redis.zincrby(name = "visit", value = id, amount = 1)
	visit = Redis.zscore(name = "visit", value = id)

	dic = {}
	for i in papers:
		if i['year'] in dic:
			dic[i['year']] += 1
		else:
			dic[i['year']] = 1
	if scholar.website == None or scholar.website == "":
		website = ""
	else:
		website = scholar.website
	return JsonResponse({'name': scholar.realname, 'cite': scholar.cite, 'belong': scholar.belong, 'interest': scholar.interest,
						'website': website, 'papers': papers, 'year': dic, 'visit': int(visit)})

@csrf_exempt
def change_password(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	password = str(data_json['password'])
	newpassword1 = str(data_json['newpassword1'])
	newpassword2 = str(data_json['newpassword2'])
	id = request.session['user']
	user = User.objects.get(id = id)
	password = password[:1] + SALT1 + password[1:2] + SALT2 + password[2:-2] + SALT3 + password[-2:-1] + SALT4 + \
		password[-1:]
	password = md5(password.encode("utf8")).hexdigest()
	
	if password != user.password:
		return JsonResponse({'result': ERROR, 'message': r'密码错误'})
	if newpassword1 != newpassword2:
		return JsonResponse({'result': ERROR, 'message': r'两次密码不匹配！'})
	password = newpassword1
	password = password[:1] + SALT1 + password[1:2] + SALT2 + password[2:-2] + SALT3 + password[-2:-1] + SALT4 + \
		password[-1:]
	password = md5(password.encode("utf8")).hexdigest()
	user.password = password
	user.save()
	return JsonResponse({'result': ACCEPT, 'message': r'修改成功！'})

@csrf_exempt
def get_info(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
    id = check_session(request)
    if id == 0:
        return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    info = User.objects.get(id=id)
    # if not info.scholar:
    #     return JsonResponse({'result': ACCEPT, 'message': r'您还没有认证!'})
    return JsonResponse(
        {'result': ACCEPT, 'message': r'获取成功!', 'username': info.username, 'email': info.email, 'gender': info.gender,
         'area': info.area, 'phone': info.phone})

@csrf_exempt
def set_info(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
    id = check_session(request)
    if id == 0:
        return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    data_json = json.loads(request.body)
    info = User.objects.get(id=id)
    info.email = data_json['email']
    info.gender = data_json['gender']
    info.area = data_json['area']
    info.phone = data_json['phone']
    info.save()
    return JsonResponse(
        {'result': ACCEPT, 'message': r'修改成功!'})

@csrf_exempt
def create_scholar_info(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'你在干嘛'})
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	realname = data_json.get('realname', "")
	belong = data_json.get('belong', "")
	interest = data_json.get('interest', "")
	if Scholar.objects.filter(uid = id).exists() == False:
		scholar = Scholar()
		scholar.uid = id
	else:
		scholar = Scholar.objects.get(uid = id)
	scholar.realname = realname
	scholar.belong = belong
	scholar.interest = interest
	scholar.save()
	return JsonResponse({'result': ACCEPT, 'message': r'设置成功！'})

@csrf_exempt
def logout(request):
    if request.session.get('user', -1) != -1:
        request.session.flush()
        return JsonResponse({'result': ACCEPT, 'message': r'已登出!'})
    else:
        return JsonResponse({'result': ERROR, 'message': r'请先登录!'})

@csrf_exempt
def set_profile(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'????'})
    id = check_session(request)
    if id == 0:
        return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    file = request.FILES.get('file', None)
    # name = request.POST.get('name')
    if not file:
        return JsonResponse({'result': ERROR, 'message': r'设置失败！'})
    filename, type = os.path.splitext(file.name)
    if type != '.jpg' and type != '.png':
        return JsonResponse({'result': ERROR, 'message': r'请上传JPG或PNG格式图片！'})
    profile = str(id) + type
    user = User.objects.get(id=id)
    user.profile = profile
    user.save()
    with open(os.path.join(MEDIA_ROOT, profile).replace('\\', '/'), "wb") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return JsonResponse({'result': ACCEPT, 'message': r'设置成功! '})


@csrf_exempt
def get_profile(request):
    if request.method == 'POST':
        return JsonResponse({'result': ERROR, 'message': r'????'})
    # id = check_session(request)
    # if id == 0:
    #     return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    # filename = request.GET.get('img_name')
    # try:
    #     file = open(os.path.join(MEDIA_ROOT, filename).replace('\\', '/'), 'wb')
    #     response = FileResponse(file)
    #     response['Content-Type'] = 'image/' + os.path.splitext(filename)[1]
    #     return response
    # except FileNotFoundError:
    #     file = open(os.path.join(MEDIA_ROOT, "default_profile.png").replace('\\', '/'), 'wb')
    #     response = FileResponse(file)
    #     response['Content-Type'] = 'image/' + os.path.splitext(filename)[1]
    #     return response

    try:
        data = request.GET
        id = data.get("id")
        file_name = User.objects.get(id=id).profile
        imagepath = os.path.join(MEDIA_ROOT, file_name).replace('\\', '/')  # 图片路径
        # with open(imagepath, 'rb') as f:
        f = open(imagepath, 'rb')
        image_data = f.read()
        return HttpResponse(image_data, content_type="image/"+file_name[-3:])
    except Exception as e:
        imagepath = os.path.join(MEDIA_ROOT, 'default_profile.png').replace('\\', '/')  # 图片路径
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data,  content_type="image/png")


@csrf_exempt
def find_scholar(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'????'})
    data_json = json.loads(request.body)
    res = []
    for i in Scholar.objects.filter(realname__icontains=data_json['name']):
        if User.objects.get(id=i.uid).scholar:
            res.append(i.to_dic())
    # res = [x.to_dic() for x in Scholar.objects.filter(realname__icontains=data_json['name'])]
    return JsonResponse({'result': ACCEPT, 'message': r'获取成功! ', 'list': res})


@csrf_exempt
def upload_img(request):
    if request.method != 'POST':
        return JsonResponse({'result': ERROR, 'message': r'????'})
    id = check_session(request)
    if id == 0:
        return JsonResponse({'result': ERROR, 'message': r'请先登录'})
    file = request.FILES.get('file', None)
    if not file:
        return JsonResponse({'result': ERROR, 'message': r'上传失败！'})
    file = request.FILES.get('file', None)
    filename = ''
    if file:
        _, type = os.path.splitext(file.name)
        if type != '.jpg' and type != '.png':
            return JsonResponse({'result': ERROR, 'message': r'请上传JPG或PNG格式图片！'})
        filename = "ma" + str(id) + "_" + str(uuid.uuid1()) + type
        with open(os.path.join(MEDIA_ROOT, filename).replace('\\', '/'), "wb") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    return JsonResponse({'result': ACCEPT, 'message': r'上传成功！', 'url': r'/message/look_feedback_img?file_name='+filename})

@csrf_exempt
def cancel_scholar(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	id = check_session(request)
	if id != 1:
		return JsonResponse({'result': ERROR, 'message': r'权限错误'})
	uid = int(data_json.get('uid', 1))
	user = User.objects.get(id = uid)
	if user.scholar == False:
		return JsonResponse({'result': ACCEPT, 'message': r'该用户已经不是学者！'})
	user.scholar = False
	user.save()
	
	scholar = Scholar.objects.get(uid = uid)
	scholar.cite = 0
	scholar.save()

	claims = [x for x in Claim.objects.filter(uid = uid)]
	for i in claims:
		author_list = [j.author for j in AuthorInfo.objects.filter(pid = i.pid)]
		for j in author_list:
			if difflib.SequenceMatcher(lambda x:x == " ", name.lower(), j.lower()).ratio() >= 0.9:
				name = j
				break
		while name in author_list:
			author_list.remove(name)
		for author_name in author_list:
			if Relation.objects.filter(name1=name, name2=author_name).exists() == True:
				r1 = Relation.objects.get(name1=name, name2=author_name)
				r1.delete()
			if Relation.objects.filter(name1=author_name, name2=name).exists() == True:
				r2 = Relation.objects.get(name1=author_name, name2=name)
				r2.delete()
		i.delete()
	# Delete claim and relation

	scholar.delete()
	# Delete all information

	feedback = Feedback(
		uid = uid,
		mid = 0,
		type = 7,
		isdeal = True,
		date = str(datetime.now())[:19]
	)
	feedback.save()
	return JsonResponse({'result': ACCEPT, 'message': r'已取消该用户学者身份！'})

#
# @csrf_exempt
# def get_img(request):
#     if request.method == 'POST':
#         return JsonResponse({'result': ERROR, 'message': r'????'})
#     data = request.GET
#     file_name = data.get("file_name")
#     imagepath = os.path.join(MEDIA_ROOT, file_name).replace('\\', '/')  # 图片路径
#     try:
#         # with open(imagepath, 'rb') as f:
#         f = open(imagepath, 'rb')
#         image_data = f.read()
#         return HttpResponse(image_data, content_type="image/" + file_name[-3:])
#     except Exception as e:
#         imagepath = os.path.join(MEDIA_ROOT, 'default_profile.png').replace('\\', '/')  # 图片路径
#         with open(imagepath, 'rb') as f:
#             image_data = f.read()
#         return HttpResponse(image_data, content_type="image/png")
