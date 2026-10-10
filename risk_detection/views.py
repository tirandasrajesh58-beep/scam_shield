from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileAnalysisForm
from .services.profile_ml import predict_profile_risk_ml
from dashboard.models import AnalysisRecord

def profile_analyze(request):
    """
    Evaluates social media profile risk using trained Random Forest ML + Explainable heuristics.
    Saves analysis to AnalysisRecord for logged-in users.
    """
    result = None
    saved_record = None

    if request.method == 'POST':
        form = ProfileAnalysisForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = predict_profile_risk_ml(data)

            # Persist to database if authenticated
            if request.user.is_authenticated:
                saved_record = AnalysisRecord.objects.create(
                    user=request.user,
                    analysis_type='PROFILE',
                    input_summary=f"@{data['username']}",
                    risk_score=result['risk_score'],
                    risk_level=result['risk_level'],
                    confidence=result['confidence'],
                    reasons=result['reasons'],
                    factor_weights=result['factor_weights'],
                    recommendation=result['recommendation'],
                    raw_data={
                        'input': {
                            'username': data['username'],
                            'display_name': data.get('display_name'),
                            'followers': data['followers'],
                            'following': data['following'],
                            'posts': data['posts'],
                            'account_age_days': data['account_age_days'],
                            'is_verified': data['is_verified'],
                            'has_profile_pic': data['has_profile_pic'],
                            'external_link': data.get('external_link'),
                            'bio': data.get('bio'),
                        },
                        'features': result['raw_features']
                    }
                )
                messages.success(request, f"Assessment for @{data['username']} completed and recorded to your threat history.")
            else:
                messages.info(request, "Assessment completed. Log in to permanently save your threat logs.")
    else:
        form = ProfileAnalysisForm()

    context = {
        'form': form,
        'result': result,
        'saved_record': saved_record,
    }
    return render(request, 'risk_detection/profile_analysis.html', context)


def message_analyze(request):
    """Placeholder for scam message NLP analyzer (Phase 8)."""
    return render(request, 'landing.html')
