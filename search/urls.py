from django.urls import path
from search.views import *

urlpatterns = [
	path('normal', search),
	path('get_history', get_history),
	path('del_history', del_history),
]