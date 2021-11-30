from django.shortcuts import render
from paper.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from user.views import *
import json
import arxiv
# Create your views here.

def create_paper(info):
	paper = Paper(title = info['title'])
	if info.get('year', '') != '':
		paper.year = info['year']
	if info.get('cite', '') != '':
		paper.cite = info['cite']
	if info.get('url', []) != []:
		url = info['url']
		url = MAGIC.join(url)
		paper.url = url
	if info.get('field', []) != []:
		field = info['field']
		field = MAGIC.join(field)
		paper.field = field
	if info.get('keyword', []) != []:
		keyword = info['keyword']
		keyword = MAGIC.join(keyword)
		paper.keyword = keyword
	paper.venue = info.get('venue', '')
	paper.abstract = info.get('abstract', '')
	paper.lang = info.get('lang', '')
	paper.doi = info.get('doi', '')
	paper.save()
	authors = info.get('author', [])
	for x in range(len(authors)):
		author = AuthorInfo(pid = paper.id, author = authors[x], rank = x)
		author.save()
	return paper.id

@csrf_exempt
def claim_paper(request):
	if request.method == 'POST':
		uid = request.session.get('user', -1)
		data_json = json.loads(request.body)
		paper = data_json.get('paper', {})
		if Paper.objects.filter(title = paper['title']).exists() == False:
			pid = create_paper(paper)
		else:
			pid = Paper.objects.get(title = paper['title'])
		claim = Claim(uid = uid, pid = pid)
		claim.save()
		return JsonResponse({'result': ACCEPT, 'message': r'认领成功！'})

@csrf_exempt
def download(request):
	if request.method == 'POST':
		id = check_session(request)
		if id == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		data_json = json.loads(request.body)
		if data_json.get('title', -1) != -1:
			title = data_json.get('title')
		else:
			pid = int(data_json.get('pid'))
			paper = Paper.objects.get(id = pid)
			title = paper.title

		search = arxiv.Search(
			query = title,
			max_results = 1,
			sort_by = arxiv.SortCriterion.Relevance
		)

		for result in search.results():
			url = result.pdf_url
		return JsonResponse({'result':'ACCEPT', 'message':r'获取成功', 'url':url})
		