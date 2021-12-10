from django.urls import path
from paper.views import *

urlpatterns = [
	path('claim_paper', claim_paper),
	path('download', download),
	path('get_cite', get_cite),
	path('get_hot_field', get_hot_field),
	path('comment', comment),
	path('get_comments', get_comments),
	path('favor', favor),
	path('get_favor_list', get_favor_list),
	path('undo_favor', undo_favor),
]