from typing import Any, Dict
from django.views import generic
from django.shortcuts import get_object_or_404, render
from .models import Lampi
from django.http import FileResponse, Http404
import os

class StartGameView(generic.TemplateView):
    template_name = 'KTALDE_web/startgame.html'


class IndexView(generic.TemplateView):
    template_name = 'KTALDE_web/index.html'


class DetailView(generic.TemplateView):
    template_name = 'KTALDE_web/detail.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(DetailView, self).get_context_data(**kwargs)
        context['device'] = get_object_or_404(
            Lampi, pk=kwargs['device_id'], user=self.request.user)
        print("CONTEXT: {}".format(context))
        return context
    
def view_pdf(request):
    try:
        # Open the PDF file in binary read mode
        file_path = os.path.join('static/KTALDE_web/pdf/ExpertInstructions.pdf')
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404("PDF not found")