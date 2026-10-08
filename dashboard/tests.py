from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from dashboard.models import AnalysisRecord

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='analyst1', password='Password123!')
        self.user2 = User.objects.create_user(username='analyst2', password='Password123!')

        self.record1 = AnalysisRecord.objects.create(
            user=self.user1,
            analysis_type='PROFILE',
            input_summary='@crypto_giveaway_bot',
            risk_score=88,
            risk_level='HIGH_RISK',
            confidence=94.5,
            reasons=['Zero posts with 5,000 following', 'Account created yesterday'],
            factor_weights={'Follow ratio': 30, 'Account age': 25},
            recommendation='Do not engage. Probable fraudulent bot.'
        )

        self.record2 = AnalysisRecord.objects.create(
            user=self.user2,
            analysis_type='MESSAGE',
            input_summary='You won Rs 50,000! Click here immediately',
            risk_score=95,
            risk_level='HIGH_RISK',
            confidence=98.0,
            reasons=['Urgency keyword detected', 'Financial lure detected'],
            factor_weights={'Urgency': 40, 'Lure': 40},
            recommendation='Block sender and report phishing.'
        )

    def test_dashboard_kpis_and_context(self):
        """Verify dashboard view computes proper counts for user1."""
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 1)
        self.assertEqual(response.context['high_risk_count'], 1)
        self.assertEqual(response.context['safe_count'], 0)
        self.assertContains(response, '@crypto_giveaway_bot')

    def test_history_filtering(self):
        """Test history view filters by analysis_type."""
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.get(reverse('dashboard:history') + '?type=PROFILE')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['records'].count(), 1)

        response_empty = self.client.get(reverse('dashboard:history') + '?type=MESSAGE')
        self.assertEqual(response_empty.context['records'].count(), 0)

    def test_record_detail_access_control(self):
        """User 1 can see record 1; User 2 receives 404 trying to see record 1."""
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.get(reverse('dashboard:record_detail', args=[self.record1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Explainable Threat Assessment Report')

        # User 2 cannot access user 1's record
        self.client.login(username='analyst2', password='Password123!')
        response_forbidden = self.client.get(reverse('dashboard:record_detail', args=[self.record1.pk]))
        self.assertEqual(response_forbidden.status_code, 404)

    def test_record_delete(self):
        """User can delete their own record."""
        self.client.login(username='analyst1', password='Password123!')
        response = self.client.post(reverse('dashboard:record_delete', args=[self.record1.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(AnalysisRecord.objects.filter(pk=self.record1.pk).exists())
