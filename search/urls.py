from django.urls import path
from search.views import *

urlpatterns = [
	path('normal', search),
	path('advance', advance),
	path('get_history', get_history),
	path('del_history', del_history),
	path('id_search', id_search),
]