from elasticsearch import Elasticsearch
from academic.values import *

'''
需要支持的功能： 按标题等各个字段检索，多字段检索
搜索结果高亮 : 前端 
'''

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
	origin = ES.search(index='small', body=mapping)
	data = origin["aggregations"]["result"]["buckets"]
	result = [i for i in data if len(str(i['key'])) >= 3]
	if len(result) > 10:
		result = result[0:10]
	return result

def nomalSearch(title = "", author = "", abstract = "",
				page = 1):
	mapping = {
		"query": {
			"match": {}
		},
		"from": PAGE*(page-1),
		"size": PAGE*page-1
	}

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
	origin = ES.search(index='small', body=mapping)
	count_info = ES.count(index='small', body={"query" : mapping["query"]})
	count = count_info['count']
	
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	
	result = {
		"paper": papers,			# devide by page
		"total": count,
		"pages": (count + PAGE - 1) // PAGE
	}

	if page == 1:
		year_bucket = getCountData(field = field, string = string, bucket = "year")
		author_bucket = getCountData(field = field, string = string, bucket = "author")
		field_bucket = getCountData(field = field, string = string, bucket = "field")
		result["year"] = year_bucket
		result["author"] = author_bucket
		result["field"] = field_bucket
	return result
