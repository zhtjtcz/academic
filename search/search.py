from elasticsearch import Elasticsearch

def nomalSearch(mapping):
	es = Elasticsearch(
		hosts = 'localhost:9200'
	)
	
	'''
	mapping = {
		"query": {
			"match": {
				"title": "hello the beautiful world!"
			}
		},
		"highlight": {
			"fields": {
				"title": {}
			}
		}
	}
	'''

	result = es.search(index='test', body=mapping)
	return result