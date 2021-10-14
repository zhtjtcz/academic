from django.shortcuts import render
from paper.models import *
from academic.values import *
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