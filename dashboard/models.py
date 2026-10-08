from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class AnalysisRecord(models.Model):
    """
    Central database model storing threat analysis history across all Scam Shield modules.
    Ensures per-user data isolation and fast querying for dashboard analytics.
    """
    ANALYSIS_TYPE_CHOICES = [
        ('PROFILE', 'Fake Profile Detection'),
        ('MESSAGE', 'Scam Message NLP'),
        ('IMPERSONATION', 'Impersonation Detection'),
        ('APP', 'Mobile APK Analysis'),
    ]

    RISK_LEVEL_CHOICES = [
        ('SAFE', 'Safe / Low Risk (0–39)'),
        ('SUSPICIOUS', 'Suspicious / Medium Risk (40–69)'),
        ('HIGH_RISK', 'High Risk (70–100)'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analyses',
        help_text="The analyst/user who conducted this analysis."
    )
    analysis_type = models.CharField(
        max_length=20,
        choices=ANALYSIS_TYPE_CHOICES,
        db_index=True
    )
    input_summary = models.CharField(
        max_length=255,
        help_text="Short label or identifier (e.g. username, message excerpt, APK name)."
    )
    risk_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Standardized risk score from 0 to 100."
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        db_index=True
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Model/heuristic confidence percentage (0.0 to 100.0)."
    )
    reasons = models.JSONField(
        default=list,
        help_text="List of explainable risk factors."
    )
    factor_weights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contribution weights of individual features."
    )
    recommendation = models.TextField(
        blank=True,
        help_text="Actionable security recommendation."
    )
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete input attributes and raw model metadata."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'analysis_type']),
            models.Index(fields=['user', 'risk_level']),
        ]

    def __str__(self):
        return f"[{self.get_analysis_type_display()}] {self.input_summary} - Score {self.risk_score} ({self.risk_level})"

    @property
    def badge_class(self):
        """Returns the CSS class for styling risk badges."""
        if self.risk_level == 'SAFE':
            return 'risk-safe'
        elif self.risk_level == 'SUSPICIOUS':
            return 'risk-suspicious'
        return 'risk-high'

    @property
    def type_icon(self):
        """Returns the Bootstrap icon name for the analysis type."""
        icons = {
            'PROFILE': 'bi-person-badge',
            'MESSAGE': 'bi-chat-left-dots',
            'IMPERSONATION': 'bi-people',
            'APP': 'bi-file-earmark-code',
        }
        return icons.get(self.analysis_type, 'bi-shield-check')
