def check_session(request):
	id = request.session.get('user', 0)
	return id