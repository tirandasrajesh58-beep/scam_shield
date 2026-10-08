from django.shortcuts import render

def analyze(request):
    return render(request, 'landing.html')
