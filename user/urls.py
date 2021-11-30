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
	path('change_password', change_password)
]