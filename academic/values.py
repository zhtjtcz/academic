from elasticsearch import Elasticsearch
import os
import platform

ERROR = 0
ACCEPT = 1

INTO_TEMPLATE_MD = "# 个人简介 \n 无"
INTO_TEMPLATE_HTML = '<h1><a id="_0"></ a>个人简介</h1> <p>无</p > '

MAGIC = "s~8>1)"

SALT1 = 'a'
SALT2 = 'w'
SALT3 = '1'
SALT4 = '7'

if platform.system() == 'Linux':
	ES = Elasticsearch(
		hosts = 'localhost:9128'
	)
else:
	ES = Elasticsearch(
		hosts = '123.60.215.20:9128'
	)

ES_INDEX = 'main'

APPEAL_PAPER = 1
APPEAL_IDENTITY = 2
CLAIM_PAPER = 3
FEEDBACK = 4
RERLY = 5

PAGE = 20

STORAGE_PATH = ''

NOT = 2
AND = 1
OR = 0

ALPHA = 0.01
BETA = 3.14159265358979 * 2.71828 * 100
