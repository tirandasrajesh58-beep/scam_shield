from django.shortcuts import render

def landing(request):
    """Landing page showcasing Scam Shield features and branding."""
    return render(request, 'landing.html')

def home(request):
    """Main cybersecurity dashboard."""
    return render(request, 'landing.html')

def history(request):
    """Analysis history view placeholder."""
    return render(request, 'landing.html')
