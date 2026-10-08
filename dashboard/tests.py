from django.test import TestCase
from django.contrib.auth.models import User
from dashboard.models import AnalysisRecord

class AnalysisRecordModelTests(TestCase):
    def setUp(self):
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

    def test_record_creation_and_properties(self):
        """Test record fields and dynamic badge helpers."""
        self.assertEqual(self.record1.badge_class, 'risk-high')
        self.assertEqual(self.record1.type_icon, 'bi-person-badge')
        self.assertIn('@crypto_giveaway_bot', str(self.record1))

    def test_user_data_isolation(self):
        """Verify analyst 1 only retrieves their own records."""
        user1_records = AnalysisRecord.objects.filter(user=self.user1)
        self.assertEqual(user1_records.count(), 1)
        self.assertEqual(user1_records.first().input_summary, '@crypto_giveaway_bot')

        user2_records = AnalysisRecord.objects.filter(user=self.user2)
        self.assertEqual(user2_records.count(), 1)
        self.assertEqual(user2_records.first().input_summary, 'You won Rs 50,000! Click here immediately')
