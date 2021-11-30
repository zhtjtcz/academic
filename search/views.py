from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from .search import *
import json


# Create your views here.

@csrf_exempt
def search(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		title = data_json.get('title', "")
		author = data_json.get('author', "")
		abstract = data_json.get('abstract', "")
		result = nomalSearch(title)
		return JsonResponse({'result': ACCEPT, 'message': result})
