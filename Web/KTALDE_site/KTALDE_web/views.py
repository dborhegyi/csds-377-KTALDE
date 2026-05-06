from typing import Any, Dict
from django.views import generic
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Lampi
from .forms import AddLampiForm

from django.http import FileResponse, Http404
import os

class StartGameView(generic.TemplateView, generic.FormView):
    template_name = 'KTALDE_web/startgame.html'

    # adding association code functionality according to the FormView
#    form_class = AddLampiForm
#    success_url = '/lampi'

#    def form_valid(self, form: AddLampiForm) -> HttpResponse:
#        device = form.cleaned_data['device']
#        device.associate_and_publish_associated_msg(self.request.user)
#        return super(AddLampiView, self).form_valid(form)
    def get_context_data(self, **kwargs):
        context = kwargs
        session = self.request.session

        context['form1'] = AddLampiForm()
        context['form2'] = AddLampiForm()
        context['player1_device'] = session.get('player1_device')
        context['player2_device'] = session.get('player2_device')
        context['player1_code'] = session.get('player1_code', '')
        context['player2_code'] = session.get('player2_code', '')
        context['selected_level'] = session.get('selected_level', 1)

        return context

    def form_valid(self, form: AddLampiForm) -> HttpResponse:
        device = form.cleaned_data['device']
        device.associate_and_publish_associated_msg(self.request.user)
        return HttpResponseRedirect(reverse('startgame'))

    def post(self, request, *args, **kwargs):
        player_slot = request.POST.get('player_slot')  # '1' or '2'
        form = AddLampiForm(request.POST)

        if form.is_valid():
            # Store associated device info in session before calling form_valid
            device = form.cleaned_data['device']
            request.session[f'player{player_slot}_device'] = str(device)
            request.session[f'player{player_slot}_code'] = form.cleaned_data['association_code']

            return self.form_valid(form)
        else:
            # Re-render with errors on the right form
            context = self.get_context_data()
            if player_slot == '1':
                context['form1'] = form
            else:
                context['form2'] = form
            return render(request, self.template_name, context)

def ingame(request):
    return render(request, 'KTALDE_web/ingame.html')

def gameover(request):
    return render(request, 'KTALDE_web/gameover.html')

def win(request):
    return render(request, 'KTALDE_web/win.html')


# def view_pdf(request):
#     try:
#         # Build an absolute path relative to this views.py file
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         file_path = os.path.join(base_dir, 'static', 'KTALDE_web', 'pdf', 'ExpertInstructions.pdf')
#         return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
#     except FileNotFoundError:
#         raise Http404("PDF not found")
