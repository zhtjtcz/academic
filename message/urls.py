from django.urls import path
from message.views import *

urlpatterns = [
	path('get_messages', get_messages),
	path('get_message', get_message),
	path('deal_claim', deal_claim),
]