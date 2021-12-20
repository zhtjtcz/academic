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

def getCountData(query = {}, bucket = ""):
	mapping = {
		"query": query,
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

	dic = {"type":1, "key": "", "value":""}
	if len(title) > 0:
		mapping["query"]["match"]["title"] = {
			"query": title,
			"minimum_should_match": "75%"
		}
		dic["key"] = "title"
		dic["value"] = title
	elif len(author) > 0:
		mapping["query"]["match"]["author"] = {
			"query": author,
			"minimum_should_match": "75%"
		}
		dic["key"] = "author"
		dic["value"] = author
	elif len(abstract) > 0:
		mapping["query"]["match"]["abstract"] = {
			"query": abstract,
			"minimum_should_match": "75%"
		}
		dic["key"] = "abstract"
		dic["value"] = abstract
	elif len(doi) > 0:
		mapping["query"]["match"]["doi"] = {
			"query": doi,
			"minimum_should_match": "75%"
		}
		dic["key"] = "doi"
		dic["value"] = doi
	elif len(field) > 0:
		mapping["query"]["match"]["field"] = {
			"query": field,
			"minimum_should_match": "75%"
		}
		dic["key"] = "field"
		dic["value"] = field
	elif len(keyword) > 0:
		mapping["query"]["match"]["keyword"] = {
			"query": keyword,
			"minimum_should_match": "75%"
		}
		dic["key"] = "keyword"
		dic["value"] = keyword
		Redis.zincrby(name = "keyword", value = keyword, amount = 1)
	
	newGroup = [dic]
	for x in group:
		newGroup.append(x)
		if x["type"] == OR:
			newGroup.append(dic)
	group = newGroup
	if group != []:
		logic = getLogic(group)
		mapping["post_filter"] = logic
	
	origin = ES.search(index=ES_INDEX, body=mapping)
	count_info = ES.count(index=ES_INDEX, body={"query" : logic})
	count = count_info['count']
	
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	
	result = {
		"paper": papers,			# devide by page
		"total": count,
		"pages": (count + limit - 1) // limit
	}

	if page == 1:
		year_bucket = getCountData(query = mapping["query"], bucket = "year")
		author_bucket = getCountData(query = mapping["query"], bucket = "author.raw")
		field_bucket = getCountData(query = mapping["query"], bucket = "field")
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
				x['key']: {
					"query": x['value'],
					"minimum_should_match": "75%"	
				}
			}})
	
	now = getBasicLogic()

	for x in params:
		if x['type'] == NOT:
			continue
		elif x['type'] == AND:
			now["bool"]["must"].append({
			"match": {
				x['key']: {
					"query": x['value'],
					"minimum_should_match": "75%"	
				}
			}})
		elif x['type'] == OR:
			logic["bool"]["should"].append(now)
			now = getBasicLogic()
			now["bool"]["must"].append({
			"match": {
				x['key']: {
					"query": x['value'],
					"minimum_should_match": "75%"	
				}
			}})
		else:
			print("Fuck Frontend!")
	logic["bool"]["should"].append(now)
	return logic

def advanceSearch(params, page, limit, group = []):
	logic = getLogic(params)
	mapping = {
		"query": logic,
		"from": limit*(page-1),
		"size": limit
	}

	if group != []:
		mapping["post_filter"] = getLogic(group)

	origin = ES.search(index=ES_INDEX, body = mapping)
	if group == []:
		count_info = ES.count(index=ES_INDEX, body = {"query" : mapping["query"]})
	else:
		x = mapping["post_filter"]
		y = mapping["query"]
		print(x)
		print(y)
		now = getBasicLogic()
		now["bool"]["must"].append(x)
		now["bool"]["must"].append(y)
		count_info = ES.count(index=ES_INDEX, body = {"query" : now})
	
	count = count_info['count']
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	result = {
		"paper": papers,			# devide by page
		"total": count,
		"pages": (count + 20 - 1) // 20
	}

	if page == 1:
		year_bucket = getCountData(query = mapping["query"], bucket = "year")
		author_bucket = getCountData(query = mapping["query"], bucket = "author.raw")
		field_bucket = getCountData(query = mapping["query"], bucket = "field")
		result["year"] = year_bucket
		result["author"] = author_bucket
		result["field"] = field_bucket
	
	return result
