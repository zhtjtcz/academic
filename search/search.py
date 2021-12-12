from elasticsearch import Elasticsearch
from academic.values import *
from user.views import check_session
from datetime import datetime, timedelta
from academic.settings import Redis

'''
需要支持的功能:多字段检索
'''

def update_hot(bucket, result):
	for i in result:
		Redis.zincrby(name = bucket, value = i['key'], amount = i['doc_count'])
	# Update the hot in the redis

def getCountData(field = "", string = "", bucket = ""):
	mapping = {
		"query": {
			"match": {
				field : {
					"query": string,
					"minimum_should_match": "75%"
				}
			}
		},
		"size": 0,
		"aggs": {
            "result": {
				"terms": {
					"field": bucket,
					"size": 50,
					"order": {
						"_count": "desc"
						}
				}
        	}
   		}
	}
	origin = ES.search(index=ES_INDEX, body=mapping)
	data = origin["aggregations"]["result"]["buckets"]
	result = [i for i in data if len(str(i['key'])) >= 3]
	if len(result) > 10:
		result = result[0:10]
	if bucket == "year":
		result = [i for i in result if i['key']<=2021]
	if bucket != "year":
		update_hot(bucket, result)
	return result

def nomalSearch(request = None,
				title = "", author = "", abstract = "",  doi = "", field = "", keyword = "",
				page = 1, limit = 20,
				sorted = 0, group = []):
	mapping = {
		"query": {
			"match": {}
		},
		"from": limit*(page-1),
		"size": limit
	}

	if sorted != 0:
		mapping["sort"] = []
		if abs(sorted) == 1:
			mapping["sort"].append({"year": {"order": "asc" if sorted == 1 else "desc"}})
		elif abs(sorted) == 2:
			mapping["sort"].append({"cite": {"order": "asc" if sorted == 2 else "desc"}})
	# Sort by some order

	if len(title) > 0:
		search_field = "title"
		string = title
		mapping["query"]["match"]["title"] = {
			"query": title,
			"minimum_should_match": "75%"
		}
	elif len(author) > 0:
		search_field = "author"
		string = author
		mapping["query"]["match"]["author"] = {
			"query": author,
			"minimum_should_match": "75%"
		}
	elif len(abstract) > 0:
		search_field = "abstract"
		string = abstract
		mapping["query"]["match"]["abstract"] = {
			"query": abstract,
			"minimum_should_match": "75%"
		}
	elif len(doi) > 0:
		search_field = "doi"
		string = doi
		mapping["query"]["match"]["doi"] = {
			"query": doi,
			"minimum_should_match": "75%"
		}
	elif len(field) > 0:
		search_field = "field"
		string = field
		mapping["query"]["match"]["field"] = {
			"query": field,
			"minimum_should_match": "75%"
		}
	elif len(keyword) > 0:
		search_field = "keyword"
		string = field
		mapping["query"]["match"]["keyword"] = {
			"query": keyword,
			"minimum_should_match": "75%"
		}
		Redis.zincrby(name = "keyword", value = keyword, amount = 1)
	
	if group != []:
		logic = getLogic(group)
		mapping["post_filter"] = logic

	origin = ES.search(index=ES_INDEX, body=mapping)
	count_info = ES.count(index=ES_INDEX, body={"query" : mapping["query"]})
	count = count_info['count']
	
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	
	result = {
		"paper": papers,			# devide by page
		"total": count,
		"pages": (count + limit - 1) // limit
	}

	if check_session(request) and page == 1:
		history = request.session.get('history', [])
		history.append({
				"field": search_field,
				"string": string,
				"time": str(datetime.now())[:19],
			}
		)
		if len(history) > 5:
			history.pop(0)
		request.session['history'] = history
		# Save the search history

	if page == 1:
		year_bucket = getCountData(field = search_field, string = string, bucket = "year")
		author_bucket = getCountData(field = search_field, string = string, bucket = "author.raw")
		field_bucket = getCountData(field = search_field, string = string, bucket = "field")
		result["year"] = year_bucket
		result["author"] = author_bucket
		result["field"] = field_bucket
	return result

def getBasicLogic():
	return {
		"bool": {
				"must": []
		}
	}

def getLogic(params):
	logic = {
		"bool": {
				"must_not": [],
				"should": []
		}
	}
	for x in params:
		if x['type'] != NOT:
			continue
		logic["bool"]["must_not"].append({
			"match": {
				x['key']: x['value']
			}})
	
	now = getBasicLogic()

	for x in params:
		if x['type'] == NOT:
			continue
		elif x['type'] == AND:
			now["bool"]["must"].append({
			"match": {
				x['key']: x['value']
			}})
		elif x['type'] == OR:
			logic["bool"]["should"].append(now)
			now = getBasicLogic()
			now["bool"]["must"].append({
			"match": {
				x['key']: x['value']
			}})
		else:
			print("Fuck Frontend!")
	logic["bool"]["should"].append(now)
	return logic

def advanceSearch(params, page, limit):
	logic = getLogic(params)
	mapping = {
		"query": logic,
		"from": limit*(page-1),
		"size": limit
	}
	origin = ES.search(index=ES_INDEX, body = mapping)
	count_info = ES.count(index=ES_INDEX, body = {"query" : mapping["query"]})
	
	count = count_info['count']
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	result = {
		"paper": papers,			# devide by page
		"total": count,
		"pages": (count + 20 - 1) // 20
	}
	return result
