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
		mapping = data_json.get('mapping')
		result = nomalSearch(mapping)
		return JsonResponse({'result': ACCEPT, 'message': result})
