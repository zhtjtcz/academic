from django.urls import path
from user.views import *

urlpatterns = [
	path('test', test),
	path('set_introduction', set_introduction),
	path('get_introduction', get_introduction),
	path('register', register),
	path('login', login),
	path('logout', logout),
	path('set_scholar_info', set_scholar_info),
	path('get_scholar_info', get_scholar_info),
	path('change_password', change_password),
	path('set_info', set_info),
	path('get_info', get_info),
	path('set_profile', set_profile),
	path('get_profile', get_profile),
	path('islogin', islogin),
	path('create_scholar_info', create_scholar_info),
	path('get_scholar_id', get_scholar_id),
	path('find_scholar', find_scholar),
	path('jump', jump),
	path('upload_img', upload_img),
	path('cancel_scholar', cancel_scholar),
	# path('get_img', get_img)
]
