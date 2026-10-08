from django.shortcuts import render

def profile_analyze(request):
    return render(request, 'landing.html')

def message_analyze(request):
    return render(request, 'landing.html')
