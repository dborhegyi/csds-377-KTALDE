from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

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


@login_required(login_url='login')
def detail(request, device_id):
    """View device details."""
    context = {
        'device_id': device_id,
    }
    return render(request, 'KTALDE_web/detail.html', context)


@login_required(login_url='login')
def add(request):
    """Add a new LAMPI device."""
    if request.method == 'POST':
        # Handle form submission
        return redirect('KTALDE_web:index')
    
    return render(request, 'KTALDE_web/addlampi.html')