from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.

def index(request):
    context = {
        'lampi_list': []
    }
    return render(request, 'KTALDE_web/index.html', context)