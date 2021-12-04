from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from .search import *
import json
from user.views import check_session

# Create your views here.

@csrf_exempt
def search(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		title = data_json.get('title', "")
		author = data_json.get('author', "")
		abstract = data_json.get('abstract', "")
		page = int(data_json.get('page', 1))
		limit = int(data_json.get('limit', 20))
		result = nomalSearch(request = request, title = title, author = author, abstract = abstract, page = page, limit = limit)
		return JsonResponse({'result': ACCEPT, 'message': result})

@csrf_exempt
def get_history(request):
	if request.method == 'POST':
		if check_session(request) == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		history = request.session.get('history', [])
		history.reverse()
		return JsonResponse({'result':ACCEPT, 'message': r'获取成功', 'history': history})
