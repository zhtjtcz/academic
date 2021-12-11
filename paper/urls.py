from django.urls import path
from paper.views import *

urlpatterns = [
	path('claim_paper', claim_paper),
	path('download', download),
	path('get_cite', get_cite),
	path('get_hot_field', get_hot_field),
	path('get_hot_paper', get_hot_paper),
	path('get_hot_keyword', get_hot_keyword),
	path('comment', comment),
	path('get_comments', get_comments),
	path('favor', favor),
	path('get_favor_list', get_favor_list),
	path('undo_favor', undo_favor),
	path('check_favor', check_favor),
	path('get_relation', get_relation),
	path('get_reads', get_reads),
	path('read_paper', read_paper),
	path('get_paper_info', get_paper_info),
]