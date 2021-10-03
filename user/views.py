from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from captcha.models import CaptchaStore
from academic.values import *
# Create your views here.

@csrf_exempt
def test(request):
	if request.method == 'POST':
		return JsonResponse({'result': ACCEPT, 'message': r'POST!'})
	else:
		return JsonResponse({'result': ACCEPT, 'message': r'GET!'})