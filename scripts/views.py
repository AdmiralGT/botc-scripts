from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import generic
from . import models

class ScriptsView(generic.ListView):
    template_name = "index.html"
    model = models.Script

class ScriptView(generic.DetailView):
    template_name = "script.html"
    model = models.Script
    

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
