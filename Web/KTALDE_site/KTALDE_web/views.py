from typing import Any, Dict

from django.views import generic
from django.shortcuts import get_object_or_404
from pdf_view.views import PDFView
from .models import Lampi


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
    
class MyPDFView(PDFView):
    template_name = 'KTALDE_web/instructionsPDF.html'
    title = 'My PDF Document' # optional
    filename = 'My PDF.pdf' # optional
    # css_paths = [ # optional
    #     'my_pdf/css/my_pdf.css',
    # ]