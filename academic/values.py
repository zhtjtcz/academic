from elasticsearch import Elasticsearch

ERROR = 0
ACCEPT = 1

INTO_TEMPLATE_MD = "# 个人简介 \n 无"
INTO_TEMPLATE_HTML = '<h1><a id="_0"></ a>个人简介</h1> <p>无</p > '

MAGIC = "s~8>1)"

SALT1 = 'a'
SALT2 = 'w'
SALT3 = '1'
SALT4 = '7'

ES = Elasticsearch(
	hosts = '123.60.215.20:9128'
)

APPEAL_PAPER = 1
APPEAL_IDENTITY = 2
CLAIM_PAPER = 3
FEEDBACK = 4

PAGE = 20

STORAGE_PATH = ''
