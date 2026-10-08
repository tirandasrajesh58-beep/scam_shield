from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .models import AnalysisRecord
import json

def landing(request):
    """Public landing page showcasing Scam Shield features and branding."""
    return render(request, 'landing.html')

@login_required
def home(request):
    """
    Main cybersecurity operations dashboard.
    Computes real-time threat KPIs, category distributions, and displays recent audits.
    """
    user = request.user
    user_records = AnalysisRecord.objects.filter(user=user)

    total_count = user_records.count()
    safe_count = user_records.filter(risk_level='SAFE').count()
    suspicious_count = user_records.filter(risk_level='SUSPICIOUS').count()
    high_risk_count = user_records.filter(risk_level='HIGH_RISK').count()

    avg_score_dict = user_records.aggregate(Avg('risk_score'))
    avg_score = round(avg_score_dict['risk_score__avg'] or 0, 1)

    profile_count = user_records.filter(analysis_type='PROFILE').count()
    message_count = user_records.filter(analysis_type='MESSAGE').count()
    impersonation_count = user_records.filter(analysis_type='IMPERSONATION').count()
    app_count = user_records.filter(analysis_type='APP').count()

    recent_analyses = user_records[:8]

    # Chart.js data serialized to JSON
    risk_chart_data = json.dumps([safe_count, suspicious_count, high_risk_count])
    category_chart_data = json.dumps([profile_count, message_count, impersonation_count, app_count])

    context = {
        'total_count': total_count,
        'safe_count': safe_count,
        'suspicious_count': suspicious_count,
        'high_risk_count': high_risk_count,
        'avg_score': avg_score,
        'profile_count': profile_count,
        'message_count': message_count,
        'impersonation_count': impersonation_count,
        'app_count': app_count,
        'recent_analyses': recent_analyses,
        'risk_chart_data': risk_chart_data,
        'category_chart_data': category_chart_data,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def history(request):
    """
    Full analysis history view with category and risk level filters.
    """
    user = request.user
    records = AnalysisRecord.objects.filter(user=user)

    # Filtering
    type_filter = request.GET.get('type')
    level_filter = request.GET.get('level')
    search_query = request.GET.get('q')

    if type_filter and type_filter in ['PROFILE', 'MESSAGE', 'IMPERSONATION', 'APP']:
        records = records.filter(analysis_type=type_filter)

    if level_filter and level_filter in ['SAFE', 'SUSPICIOUS', 'HIGH_RISK']:
        records = records.filter(risk_level=level_filter)

    if search_query:
        records = records.filter(input_summary__icontains=search_query)

    context = {
        'records': records,
        'selected_type': type_filter or '',
        'selected_level': level_filter or '',
        'search_query': search_query or '',
        'total_filtered': records.count(),
    }
    return render(request, 'dashboard/history.html', context)


@login_required
def record_detail(request, pk):
    """
    Detailed Explainable AI view of a single threat analysis record.
    Strictly isolated: users can only view their own analyses.
    """
    record = get_object_or_404(AnalysisRecord, pk=pk, user=request.user)
    return render(request, 'dashboard/record_detail.html', {'record': record})


@login_required
def record_delete(request, pk):
    """
    Allows analysts to delete a record they own.
    """
    record = get_object_or_404(AnalysisRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        summary = record.input_summary
        record.delete()
        messages.success(request, f"Analysis record '{summary}' was deleted successfully.")
        return redirect('dashboard:history')
    return render(request, 'dashboard/record_confirm_delete.html', {'record': record})
