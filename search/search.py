from elasticsearch import Elasticsearch

def nomalSearch(title):
	es = Elasticsearch(
		hosts = 'localhost:9200'
	)
	
	mapping = {
		"query": {
			"match": {
				"title": title
			}
		},
		"from": 0,
		"size": 100,
	}

	origin = es.search(index='small', body=mapping)
	papers = origin["hits"]["hits"]
	papers = [x for x in papers["_source"]]
	result = {
		"paper": papers,
		"total": len(papers)
	}
	return result