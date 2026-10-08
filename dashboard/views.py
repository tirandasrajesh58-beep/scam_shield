from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def landing(request):
    """Public landing page showcasing Scam Shield features and branding."""
    return render(request, 'landing.html')

@login_required
def home(request):
    """Protected main cybersecurity operations dashboard."""
    return render(request, 'dashboard/dashboard.html')

@login_required
def history(request):
    """Protected analysis history view placeholder."""
    return render(request, 'dashboard/dashboard.html')
