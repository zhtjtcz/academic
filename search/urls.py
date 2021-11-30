from django.urls import path
from search.views import *

urlpatterns = [
	path('normal', search),
]