from django.urls import path
from user.views import *

urlpatterns = [
	path('test', test),
	path('set_introduction', set_introduction),
	path('get_introduction', get_introduction),
	path('register', register),
	path('login', login),
	path('logout', logout),
]