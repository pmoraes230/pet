from django.shortcuts import render

# Create your views here.
def dash_tutor(request):
    return render(request, 'dash_tutor.html')