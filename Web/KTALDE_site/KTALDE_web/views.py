from typing import Any, Dict
from django.views import generic
from django.shortcuts import get_object_or_404, render
from .models import Lampi
from django.http import FileResponse, Http404
import os

class StartGameView(generic.TemplateView):
    template_name = 'KTALDE_web/startgame.html'

def ingame(request):
    return render(request, 'KTALDE_web/ingame.html')

# def view_pdf(request):
#     try:
#         # Build an absolute path relative to this views.py file
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         file_path = os.path.join(base_dir, 'static', 'KTALDE_web', 'pdf', 'ExpertInstructions.pdf')
#         return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
#     except FileNotFoundError:
#         raise Http404("PDF not found")