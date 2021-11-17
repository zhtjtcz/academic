from elasticsearch import Elasticsearch
from academic.values import *

'''
需要支持的功能： 按标题等各个字段检索，多字段检索，搜索结果高亮
TODO 结果高亮
'''
def nomalSearch(title = "", author = ""):
	mapping = {
		"query": {
			"match": {
				
			}
		},
		"from": 0,
		"size": 100,
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
	
	origin = ES.search(index='small', body=mapping)
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	result = {
		"paper": papers,
		"total": len(papers)
	}
	return result
