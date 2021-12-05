from django.urls import path
from myredis.views import *

urlpatterns = [
	path('test', test),
]