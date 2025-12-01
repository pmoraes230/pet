from django.shortcuts import render

# Create your views here.
def dash_vet(request):
    return render(request, 'vet_dash.html')