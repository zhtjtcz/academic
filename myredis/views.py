import os

from django import forms
from django.shortcuts import render
from message.models import Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from user.views import *
from datetime import datetime
from message.models import *
from paper.models import *
from django_redis import get_redis_connection
from django.core.cache import cache #引入缓存模块
# Create your views here.

@csrf_exempt
def test(request):
	return JsonResponse({})