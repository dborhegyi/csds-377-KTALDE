from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.

def index(request):
    context = {
        'lampi_list': []
    }
    return render(request, 'KTALDE_web/index.html', context)


class CustomLoginView(LoginView):
    template_name = 'KTALDE_web/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = '/'