from elasticsearch import Elasticsearch
from academic.values import *
from user.views import check_session
from datetime import datetime, timedelta
from academic.settings import Redis

'''
需要支持的功能：多字段检索
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
	origin = ES.search(index='marvolo', body=mapping)
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
				title = "", author = "", abstract = "",
				page = 1, limit = 20,
				sorted = 0):
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
		field = "title"
		string = title
		mapping["query"]["match"]["title"] = {
			"query": title,
			"minimum_should_match": "75%"
		}
	elif len(author) > 0:
		field = "author"
		string = author
		mapping["query"]["match"]["author"] = {
			"query": author,
			"minimum_should_match": "75%"
		}
	elif len(abstract) > 0:
		field = "abstract"
		string = abstract
		mapping["query"]["match"]["abstract"] = {
			"query": abstract,
			"minimum_should_match": "75%"
		}
	
	origin = ES.search(index='marvolo', body=mapping)
	count_info = ES.count(index='marvolo', body={"query" : mapping["query"]})
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
		history.append(
			{
				"field": field,
				"string": string,
				"time": str(datetime.now())[:19],
			}
		)
		if len(history) > 5:
			history.pop(0)
		request.session['history'] = history
		# Save the search history

	if page == 1:
		year_bucket = getCountData(field = field, string = string, bucket = "year")
		author_bucket = getCountData(field = field, string = string, bucket = "author.raw")
		field_bucket = getCountData(field = field, string = string, bucket = "field")
		result["year"] = year_bucket
		result["author"] = author_bucket
		result["field"] = field_bucket
	return result
