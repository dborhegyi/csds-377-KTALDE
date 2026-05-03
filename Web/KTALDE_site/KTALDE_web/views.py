from typing import Any, Dict
import os

from django.views import generic, View
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from django.conf import settings
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
    
class MyPDFView(View):
    pdf_filename = 'Expert Instructions.pdf'
    
    def get_pdf_path(self):
        """Get the PDF file path from various possible locations."""
        paths_to_try = [
            os.path.join(settings.BASE_DIR, self.pdf_filename),
            os.path.join(settings.BASE_DIR, 'media', self.pdf_filename),
            os.path.join(settings.BASE_DIR, 'static', self.pdf_filename),
        ]
        
        for path in paths_to_try:
            if os.path.exists(path):
                return path
        
        return paths_to_try[0]
    
    def get(self, request, response_type='pdf', **kwargs):
        pdf_path = self.get_pdf_path()
        
        try:
            pdf_file = open(pdf_path, 'rb')
        except FileNotFoundError:
            return HttpResponse(f"PDF file not found at {pdf_path}", status=404)
        
        if response_type == 'download':
            return FileResponse(
                pdf_file,
                as_attachment=True,
                filename=self.pdf_filename,
                content_type='application/pdf'
            )
        else:  # 'pdf' (inline) or 'html'
            return FileResponse(
                pdf_file,
                content_type='application/pdf'
            )