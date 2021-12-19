from django.db import transaction
from django.shortcuts import render
from paper.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *
from message.views import *
from academic.tools import check_session
import json
import arxiv
import random
from academic.settings import Redis
import difflib

# Create your views here.

def create_paper(info):
	if Paper.objects.filter(id=int(info['id'])).exists():
		paper = Paper.objects.get(id=int(info['id']))
		return paper.id

	paper = Paper(id=int(info['id']), title=info['title'])
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
		author = AuthorInfo(pid=paper.id, author=authors[x], rank=x)
		author.save()
	return paper.id


@csrf_exempt
def claim_paper(request):
	final_success = True
	one_success = False
	if request.method == 'POST':
		if check_session(request) == 0:
			return JsonResponse({'result': ERROR, 'message': r'请先登录'})
		uid = request.session['user']
		data_json = json.loads(request.body)
		papers = data_json.get('paper', [])
		for paper in papers:
			if Paper.objects.filter(id=int(paper['id'])).exists() == False:
				pid = create_paper(paper)
			else:
				pid = Paper.objects.get(id=int(paper['id'])).id
			if Claim.objects.filter(uid=uid, pid=pid).exists() == True:
				# return JsonResponse({'result': ERROR, 'message': r'您已认领该论文！'})
				final_success = False
				continue
			authors = paper['author']
			success = False
			realname = Scholar.objects.get(uid=uid).realname.lower()
			for i in authors:
				if i.lower() == realname:
					success = True
					break
			if not success:
				final_success = False
				continue
			one_success = True
			if Claim.objects.filter(uid=uid, pid=pid).exists() == False:
				claim = Claim(uid=uid, pid=pid)
				claim.save()
				user = User.objects.get(id=uid)
				user.scholar = True
				user.save()
				paper_ = Paper.objects.get(id=pid)
				scholar = Scholar.objects.get(uid=uid)
				scholar.cite += paper_.cite
				scholar.save()
			for i in range(len(authors)):
				for j in range(len(authors)):
					if i == j:
						continue
					if Relation.objects.filter(name1=authors[i], name2=authors[j]).exists():
						r = Relation.objects.get(name1=authors[i], name2=authors[j])
						r.times += 1
						r.save()
					else:
						Relation.objects.create(name1=authors[i], name2=authors[j], times=1)

					if Relation.objects.filter(name1=authors[j], name2=authors[i]).exists():
						r = Relation.objects.get(name1=authors[j], name2=authors[i])
						r.times += 1
						r.save()
					else:
						Relation.objects.create(name1=authors[j], name2=authors[i], times=1)
		if final_success:
			return JsonResponse({'result': ACCEPT, 'message': r'已完成认领！'})
		elif one_success:
			return JsonResponse({'result': ERROR, 'message': r'文章没有全部认领！'})
		else:
			return JsonResponse({'result': 2, 'message': r'所有文章认领失败！'})


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
			paper = Paper.objects.get(id=pid)
			title = paper.title

		search = arxiv.Search(
			query=title,
			max_results=1,
			sort_by=arxiv.SortCriterion.Relevance
		)

		for result in search.results():
			url = result.pdf_url
		return JsonResponse({'result': 'ACCEPT', 'message': r'获取成功', 'url': url})


@csrf_exempt
def get_cite(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		paper = data_json['paper']
		authors = ','.join(paper['author'])
		# TODO check meeting or journist
		random.seed(ord(paper['title'][0]))
		a = random.randint(10, 50)
		b = a + random.randint(1, 10)
		page = "%d(%d): %d-%d" % (random.randint(1, 10), random.randint(1, 5), a, b)
		gb = "[1] " + authors + "." + paper['title'] + "[J]." + paper['venue'] + "," + str(
			paper["year"]) + ',' + page + '.'
		bibtex = "@artical{1,\nauthor=%s,\ntitle=%s,\nyear=%d,\npages=%s,\ndoi=%s,\nurl=%s\n}" % (
			authors, paper['title'], int(paper['year']), page, paper['doi'], paper['url'][0]
		)
		return JsonResponse({'result': ACCEPT, 'gb': gb, 'bibtex': bibtex, 'paper': paper})


@csrf_exempt
def get_hot_field(request):
	result = Redis.zrevrange(name="field", start=1, end=10, withscores=True, score_cast_func=float)
	result = [{i[0]: i[1]} for i in result]
	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'hot': result})


@csrf_exempt
def get_hot_keyword(request):
	result = Redis.zrevrange(name="keyword", start=1, end=10, withscores=True, score_cast_func=float)
	result = [{i[0]: i[1]} for i in result]
	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'hot': result})


@csrf_exempt
def get_paper_info(request):
	if request.method != "POST":
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	paper = get_paper(id)
	return JsonResponse({'result': ACCEPT, 'message': r'成功', 'paper': paper})


@csrf_exempt
def get_hot_paper(request):
	# TODO del
	result = Redis.zrevrange(name="paper", start=1, end=10, withscores=True, score_cast_func=float)
	result = [x for x in result]
	clear = []
	for x in result:
		if MAGIC in x[0]:
			Redis.zrem("paper", x[0])
		else:
			clear.append(x)
	result = [{
		'title': Paper.objects.get(id=i[0]).title,
		'id': i[0],
		'hot': int(i[1]),
	} for i in clear]
	return JsonResponse({'result': result})


def get_paper(id):
	x = Paper.objects.get(id=id)
	dic = {
		'id': x.id,
		'title': x.title,
		'year': x.year,
		'cite': x.cite,
	}
	if x.url != None:
		dic['url'] = list(x.url.split(MAGIC))
	if x.field != None:
		dic['field'] = list(x.field.split(MAGIC))
	if x.keyword != None:
		dic['keyword'] = list(x.keyword.split(MAGIC))
	else:
		dic['keyword'] = []
	if x.venue != None:
		dic['venue'] = x.venue
	if x.abstract != None:
		dic['abstract'] = x.abstract
	if x.lang != None:
		dic['lang'] = x.lang
	if x.doi != None:
		dic['doi'] = x.doi
	authors = [x.author for x in AuthorInfo.objects.filter(pid=id)]
	dic['author'] = authors
	return dic


def get_papers(origin):
	result = []
	for claim in origin:
		paper_id = claim.pid
		dic = get_paper(paper_id)
		result.append(dic)
	return result


@csrf_exempt
def read_paper(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	paper = data_json.get('paper')
	paperid = create_paper(paper)
	Redis.zincrby(name="paper", value=paperid, amount=1)
	return JsonResponse({'result': ACCEPT, 'message': r'成功！'})


@csrf_exempt
def get_reads(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	id = int(data_json['id'])
	reads = Redis.zscore(name="paper", value=id)
	if reads == None:
		reads = 0
	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'reads': int(reads)})


@csrf_exempt
def favor(request):
	if request.method != 'POST':
		return
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	paper = data_json['paper']
	paper_id = create_paper(paper)
	Favor.objects.create(uid=id, pid=paper_id).save()
	with transaction.atomic():
		p = Paper.objects.get(id=paper_id)
		p.favors += 1
		p.save()
	return JsonResponse({'result': ACCEPT, 'message': r'收藏成功！'})


@csrf_exempt
def check_favor(request):
	if request.method != 'POST':
		return
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	paper_id = data_json['pid']
	favors = 0
	res = Paper.objects.filter(id=paper_id)
	if res.exists():
		favors = res[0].favors
	if not Favor.objects.filter(uid=id, pid=paper_id).exists():
		return JsonResponse({'result': ACCEPT, 'message': r'没收藏', 'r': 0, 'favors': favors})
	else:
		return JsonResponse({'result': ACCEPT, 'message': r'已收藏', 'r': 1, 'favors': favors})


@csrf_exempt
def undo_favor(request):
	if request.method != 'POST':
		return
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	paper_id = data_json['pid']
	Favor.objects.filter(uid=id, pid=paper_id).delete()
	with transaction.atomic():
		p = Paper.objects.get(id=paper_id)
		p.favors -= 1
		p.save()
	return JsonResponse({'result': ACCEPT, 'message': r'取消成功！'})


@csrf_exempt
def get_favor_list(request):
	if request.method != 'POST':
		return
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	begin = int(data_json['begin'])
	end = int(data_json['end'])

	res = [x.to_dic() for x in Favor.objects.filter(uid=id)]
	len_ = len(res)
	for x in res:
		x['paper'] = get_paper(x['pid'])

	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'list': res[begin:end], 'len': len_})


@csrf_exempt
def get_comments(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})

	data_json = json.loads(request.body)
	pid = int(data_json.get('pid', 0))
	if Comment.objects.filter(pid=pid).exists() == False:
		return JsonResponse({'result': ERROR, 'message': r'无'})
	comments = [x for x in Comment.objects.filter(pid=pid)]
	result = []
	for x in comments:
		if x.reply == 0:
			result.append({
				'id': x.id,
				'uid': x.uid,
				'pid': x.pid,
				'name': User.objects.get(id=x.uid).username,
				'time': x.time,
				'comment': x.comment,
				'son': []
			})
			for y in comments:
				if y.reply == x.id:
					result[-1]['son'].append({
						'id': y.id,
						'uid': y.uid,
						'pid': y.pid,
						'name': User.objects.get(id=y.uid).username,
						'time': y.time,
						'comment': y.comment,
						'replyname': y.replyname,
					})
	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'comments': result})


@csrf_exempt
def comment(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	id = check_session(request)
	if id == 0:
		return JsonResponse({'result': ERROR, 'message': r'请先登录'})
	data_json = json.loads(request.body)
	paper = data_json.get('paper', {})
	pid = create_paper(paper)

	comment = Comment(
		uid=id,
		pid=pid,
		time=str(datetime.now())[:19],
		comment=data_json.get('comment', ''),
		reply=int(data_json.get('reply', 0)),
		replyuid=int(data_json.get('replyuid', 0)),
		replyname=data_json.get('replyname', '')
	)
	if comment.replyuid:
		comment.replyname = User.objects.get(id=comment.replyuid).username
	comment.save()

	reply = User.objects.get(id = id).username + MAGIC + paper.title + MAGIC + data_json.get('comment', '')
	if int(data_json.get('reply', 0)) == 0:
		if Claim.objects.filter(pid = pid).exists() == True:
			l = [x for x in Claim.objects.filter(pid = pid)]
			for x in l:
				feedback = Feedback(
					uid = x.uid,
					mid = pid,
					type = RERLY,
					reply = reply,
					isdeal = 1,
					date = datetime.now(),
					url = '',
				)
				feedback.save()
	else:
		feedback = Feedback(
			uid = int(data_json.get('reply', 0)),
			mid = pid,
			type = RERLY,
			reply = reply,
			isdeal = 1,
			date = datetime.now(),
			url = '',
		)
		feedback.save()
	
	return JsonResponse({'result': ACCEPT, 'message': r'评论成功！'})


@csrf_exempt
def get_relation(request):
	if request.method != 'POST':
		return JsonResponse({'result': ERROR, 'message': r'错误'})
	data_json = json.loads(request.body)
	name = data_json['name']
	res = []
	rs = Relation.objects.filter(name1=name)
	if rs.exists():
		res = [i.to_dic() for i in rs]
	scholar = [(i.realname.lower(), i.uid) for i in Scholar.objects.all()]
	for x in res:
		name = x['name'].lower()
		for y in scholar:
			if difflib.SequenceMatcher(lambda x:x == " ", name, y[0]).ratio() >= 0.9:
				x['id'] = y[1]
				break
		else:
			x['id'] = 0
	return JsonResponse({'result': ACCEPT, 'message': r'获取成功！', 'list': res})
