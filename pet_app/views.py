from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'tela_inicio/index.html')

def login_page(request):
    return render(request, 'login/login.html')