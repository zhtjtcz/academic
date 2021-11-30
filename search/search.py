from elasticsearch import Elasticsearch
from academic.values import *

'''
需要支持的功能： 按标题等各个字段检索，多字段检索
搜索结果高亮 : 前端 
'''

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
		mapping["query"]["match"]["title"] = {
			"query": title,
			"minimum_should_match": "75%"
		}
	elif len(author) > 0:
		mapping["query"]["match"]["author"] = {
			"query": author,
			"minimum_should_match": "75%"
		}
	elif len(abstract) > 0:
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
	return result
