from django.urls import path
from message.views import *

urlpatterns = [
	path('get_messages', get_messages),
	path('get_message', get_message),
	path('deal_claim', deal_claim),
	path('feedback', feedback),
	path('upload_file', upload_file),
	path('download_file', download_file),
	path('appeal_user', appeal_user),
	path('appeal_paper', appeal_paper),
]