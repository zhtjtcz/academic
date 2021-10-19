from django.urls import path
from paper.views import *

urlpatterns = [
	path('claim_paper', claim_paper),
	path('download', download),
]