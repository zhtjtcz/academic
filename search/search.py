from elasticsearch import Elasticsearch
from academic.values import *

def nomalSearch(title):
	mapping = {
		"query": {
			"fuzzy": {
				"title": title
			}
		},
		"from": 0,
		"size": 100,
	}

	origin = ES.search(index='small', body=mapping)
	papers = origin["hits"]["hits"]
	papers = [x["_source"] for x in papers]
	result = {
		"paper": papers,
		"total": len(papers)
	}
	return result
