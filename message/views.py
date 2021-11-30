from django.shortcuts import render
from message.models import Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from academic.values import *

# Create your views here.

