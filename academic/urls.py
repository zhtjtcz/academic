"""academic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf.urls import url
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Academic API",
        default_version='v1',
        description="Welcome to the world of Tweet",
        terms_of_service="https://www.tweet.org",
        contact=openapi.Contact(email="demo@tweet.org"),
        license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
	path('user/', include(('user.urls', 'user'), namespace="user")),
	path('search/', include(('search.urls', 'search'), namespace="search")),
	path('paper/', include(('paper.urls', 'paper'), namespace="paper")),
	path('message/', include(('message.urls', 'message'), namespace="message")),
	path('myredis/', include(('myredis.urls', 'myredis'), namespace="myredis")),
	# path('captcha/', include('captcha.urls')),
	# url(r'^img/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
]
