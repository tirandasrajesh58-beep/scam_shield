/**
 * Scam Shield - Frontend JavaScript Helpers
 * Detect. Protect. Trust.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Helper: dynamic risk score badge styling
    window.getRiskBadge = function (score) {
        if (score < 40) {
            return '<span class="risk-badge risk-safe"><i class="bi bi-shield-check"></i> Safe / Low Risk</span>';
        } else if (score < 70) {
            return '<span class="risk-badge risk-suspicious"><i class="bi bi-exclamation-triangle"></i> Suspicious</span>';
        } else {
            return '<span class="risk-badge risk-high"><i class="bi bi-shield-slash"></i> High Risk</span>';
        }
    };
});
