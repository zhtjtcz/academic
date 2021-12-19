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
		field = data_json.get('field', "")
		doi = data_json.get('doi', "")
		keyword = data_json.get('keyword', "")
		page = int(data_json.get('page', 1))
		limit = int(data_json.get('limit', 20))
		sorted = int(data_json.get('sorted', 0))
		group = data_json.get('group', [])
		result = nomalSearch(request = request, title = title, author = author, abstract = abstract, field = field, doi = doi, keyword = keyword,
			page = page, limit = limit, sorted = sorted, group = group)
		return JsonResponse({'result': ACCEPT, 'message': result})

@csrf_exempt
def get_history(request):
	if request.method == 'POST':
		if check_session(request) == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		history = request.session.get('history', [])
		history.reverse()
		return JsonResponse({'result':ACCEPT, 'message': r'获取成功', 'history': history})

@csrf_exempt
def del_history(request):
	if request.method == 'POST':
		if check_session(request) == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		data_json = json.loads(request.body)
		history = request.session.get('history')
		id = len(request.session['history']) - 1 - int(data_json.get('id', 0))
		history.pop(id)
		request.session['history'] = history
		return JsonResponse({'result':ACCEPT, 'message': r'已删除'})

@csrf_exempt
def advance(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	params = data_json.get('params', [])
	page = int(data_json.get('page', 1))
	limit = int(data_json.get('limits', 20))
	result = advanceSearch(params, page, limit)
	return JsonResponse({'result': ACCEPT, 'message': result})

@csrf_exempt
def id_search(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	mapping = {
		"query": {
			"match": {"id": id}
		},
		"from": 0,
		"size": 1
	}
	origin = ES.search(index=ES_INDEX, body=mapping)
	paper = origin["hits"]["hits"]
	paper = [x["_source"] for x in paper]
	return JsonResponse({'result': ACCEPT, 'paper': paper})
