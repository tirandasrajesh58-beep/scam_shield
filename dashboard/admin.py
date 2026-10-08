from django.contrib import admin
from .models import AnalysisRecord

@admin.register(AnalysisRecord)
class AnalysisRecordAdmin(admin.ModelAdmin):
    list_display = (
        'input_summary',
        'analysis_type',
        'user',
        'risk_score',
        'risk_level',
        'confidence',
        'created_at'
    )
    list_filter = ('analysis_type', 'risk_level', 'created_at')
    search_fields = ('input_summary', 'user__username', 'recommendation')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
