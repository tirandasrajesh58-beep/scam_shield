from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from risk_detection.services.profile_rules import extract_profile_features, analyze_profile_heuristics
from dashboard.models import AnalysisRecord

class ProfileHeuristicsAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='analyst_profile', password='Password123!')

    def test_feature_extraction(self):
        """Test feature extraction helper."""
        data = {
            'username': 'crypto_bot123',
            'display_name': 'Crypto Bot',
            'followers': 10,
            'following': 500,
            'posts': 2,
            'account_age_days': 5,
            'is_verified': False,
            'has_profile_pic': True,
            'external_link': 'https://t.me/cryptobot',
            'bio': 'DM on Telegram for forex'
        }
        feat = extract_profile_features(data)
        self.assertEqual(feat['username'], 'crypto_bot123')
        self.assertTrue(feat['is_suspicious_link'])
        self.assertIn('crypto', feat['matched_user_keywords'])
        self.assertIn('telegram', feat['matched_bio_keywords'])

    def test_suspicious_profile_heuristics(self):
        """Suspicious bot profile must be flagged as HIGH_RISK."""
        data = {
            'username': 'official_crypto_giveaway_99',
            'display_name': 'Official Giveaway Support',
            'followers': 10,
            'following': 4000,
            'posts': 1,
            'account_age_days': 2,
            'is_verified': False,
            'has_profile_pic': False,
            'external_link': 'https://bit.ly/free-prize',
            'bio': 'DM on telegram @giveaway for 50000 cash prize bonus'
        }
        res = analyze_profile_heuristics(data)
        self.assertEqual(res['risk_level'], 'HIGH_RISK')
        self.assertGreaterEqual(res['risk_score'], 70)
        self.assertTrue(len(res['reasons']) > 0)

    def test_genuine_profile_heuristics(self):
        """Established verified profile must be assessed as SAFE."""
        data = {
            'username': 'nasa',
            'display_name': 'NASA',
            'followers': 500000,
            'following': 200,
            'posts': 3000,
            'account_age_days': 3000,
            'is_verified': True,
            'has_profile_pic': True,
            'external_link': 'https://nasa.gov',
            'bio': 'National Aeronautics and Space Administration official channel.'
        }
        res = analyze_profile_heuristics(data)
        self.assertEqual(res['risk_level'], 'SAFE')
        self.assertLess(res['risk_score'], 40)

    def test_profile_analyze_view_creates_record(self):
        """Logged-in user running analysis creates a persistent AnalysisRecord."""
        self.client.login(username='analyst_profile', password='Password123!')
        response = self.client.post(reverse('risk_detection:profile_analyze'), {
            'username': 'suspicious_user_88',
            'display_name': 'Quick Cash',
            'followers': 5,
            'following': 2500,
            'posts': 0,
            'account_age_days': 2,
            'bio': 'DM on whatsapp for quick cash prize',
            'external_link': 'https://t.me/claim',
            'is_verified': False,
            'has_profile_pic': False
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AnalysisRecord.objects.filter(user=self.user, input_summary='@suspicious_user_88').exists())
        record = AnalysisRecord.objects.get(user=self.user, input_summary='@suspicious_user_88')
        self.assertEqual(record.risk_level, 'HIGH_RISK')
