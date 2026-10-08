import re

SUSPICIOUS_USERNAME_KEYWORDS = [
    'official', 'admin', 'support', 'helpdesk', 'giveaway', 'crypto',
    'bonus', 'claim', 'service', 'verify', 'winner', 'rewards', 'security_team'
]

SUSPICIOUS_BIO_KEYWORDS = [
    'telegram', 't.me', 'wa.me', 'whatsapp', 'dm for', 'forex', 'crypto',
    'investment', 'double your', 'guaranteed', 'cash prize', 'lottery',
    'contact manager', 'passive income', 'click link', 'promo'
]

SHORTENER_DOMAINS = [
    'bit.ly', 'tinyurl.com', 't.me', 'wa.me', 'is.gd', 'cutt.ly', 'goo.gl', 'ow.ly'
]


def extract_profile_features(data):
    """
    Extracts numerical and categorical heuristic signals from raw profile inputs.
    """
    username = (data.get('username') or '').strip().lower()
    display_name = (data.get('display_name') or '').strip()
    followers = max(0, int(data.get('followers') or 0))
    following = max(0, int(data.get('following') or 0))
    posts = max(0, int(data.get('posts') or 0))
    account_age_days = max(0, int(data.get('account_age_days') or 0))
    is_verified = bool(data.get('is_verified'))
    has_profile_pic = bool(data.get('has_profile_pic'))
    external_link = (data.get('external_link') or '').strip().lower()
    bio = (data.get('bio') or '').strip().lower()

    # Ratios
    following_follower_ratio = following / (followers + 1)
    posts_per_day = posts / max(account_age_days, 1)

    # Username heuristics
    digits_count = sum(c.isdigit() for c in username)
    digits_ratio = digits_count / max(len(username), 1)
    matched_user_keywords = [kw for kw in SUSPICIOUS_USERNAME_KEYWORDS if kw in username]

    # Bio heuristics
    matched_bio_keywords = [kw for kw in SUSPICIOUS_BIO_KEYWORDS if kw in bio]

    # External link check
    is_suspicious_link = any(dom in external_link for dom in SHORTENER_DOMAINS)

    # Profile completeness (0 - 100)
    completeness = 0
    if has_profile_pic:
        completeness += 30
    if len(bio) > 10:
        completeness += 30
    if display_name:
        completeness += 20
    if posts > 0:
        completeness += 20

    return {
        'username': username,
        'display_name': display_name,
        'followers': followers,
        'following': following,
        'posts': posts,
        'account_age_days': account_age_days,
        'is_verified': is_verified,
        'has_profile_pic': has_profile_pic,
        'external_link': external_link,
        'bio': bio,
        'following_follower_ratio': round(following_follower_ratio, 2),
        'posts_per_day': round(posts_per_day, 3),
        'digits_ratio': round(digits_ratio, 2),
        'matched_user_keywords': matched_user_keywords,
        'matched_bio_keywords': matched_bio_keywords,
        'is_suspicious_link': is_suspicious_link,
        'completeness': completeness,
    }


def analyze_profile_heuristics(data):
    """
    Unified Explainable Heuristic Engine for Social Media Profiles.
    Returns standard Scam Shield risk schema:
    {
        'risk_score': 0-100,
        'risk_level': 'SAFE'|'SUSPICIOUS'|'HIGH_RISK',
        'confidence': float,
        'reasons': [str],
        'factor_weights': {str: int},
        'recommendation': str,
        'raw_features': dict
    }
    """
    feat = extract_profile_features(data)

    score = 15  # baseline initial risk
    reasons = []
    factor_weights = {}

    # 1. Account Age Risk
    if feat['account_age_days'] < 7:
        score += 25
        reasons.append(f"Account is extremely new ({feat['account_age_days']} days old)")
        factor_weights['Account Age (< 7 days)'] = 25
    elif feat['account_age_days'] < 30:
        score += 15
        reasons.append(f"Account is less than a month old ({feat['account_age_days']} days)")
        factor_weights['Account Age (< 30 days)'] = 15
    elif feat['account_age_days'] > 730 and feat['followers'] > 500:
        score -= 15
        factor_weights['Established Account Longevity'] = -15

    # 2. Following / Follower Anomaly
    if feat['following'] > 500 and feat['followers'] < 50:
        score += 25
        reasons.append(f"Mass following ({feat['following']}) with negligible followers ({feat['followers']})")
        factor_weights['High Following/Follower Asymmetry'] = 25
    elif feat['following_follower_ratio'] > 10.0:
        score += 15
        reasons.append(f"Abnormally high following ratio ({feat['following_follower_ratio']}x)")
        factor_weights['High Following Ratio'] = 15
    elif feat['followers'] > 2000 and feat['following'] < 500:
        score -= 10
        factor_weights['Organic Follower Surplus'] = -10

    # 3. Posts & Activity Frequency
    if feat['posts'] == 0 and feat['account_age_days'] > 14:
        score += 15
        reasons.append("Zero posts published despite established account age")
        factor_weights['Zero Post Activity'] = 15
    elif feat['posts_per_day'] > 25:
        score += 15
        reasons.append(f"High automated posting velocity ({feat['posts_per_day']} posts/day)")
        factor_weights['Automated Posting Frequency'] = 15

    # 4. Username Patterns
    if feat['digits_ratio'] >= 0.4:
        score += 15
        reasons.append(f"High proportion of numeric digits in username ({int(feat['digits_ratio']*100)}%)")
        factor_weights['Username Digits Heuristic'] = 15

    if feat['matched_user_keywords']:
        score += 18
        keywords_str = ', '.join(feat['matched_user_keywords'][:3])
        reasons.append(f"Username contains impersonation/lure keywords ({keywords_str})")
        factor_weights['Suspicious Username Keywords'] = 18

    # 5. Bio Patterns
    if feat['matched_bio_keywords']:
        score += 20
        bio_kw_str = ', '.join(feat['matched_bio_keywords'][:3])
        reasons.append(f"Bio contains financial lure or off-platform lures ({bio_kw_str})")
        factor_weights['Suspicious Bio Terminology'] = 20

    # 6. Profile Completeness & Avatar
    if not feat['has_profile_pic']:
        score += 15
        reasons.append("Default or missing profile photo (common with automated bots)")
        factor_weights['Missing Profile Photo'] = 15

    if feat['completeness'] < 40:
        score += 10
        reasons.append(f"Incomplete profile metadata ({feat['completeness']}% completeness)")
        factor_weights['Low Profile Completeness'] = 10

    # 7. External Link Check
    if feat['is_suspicious_link']:
        score += 18
        reasons.append("External link redirects to URL shortener or off-platform messenger")
        factor_weights['High Risk External URL'] = 18

    # 8. Verified Platform Dampener
    if feat['is_verified']:
        score -= 40
        reasons.append("Official verified account badge detected")
        factor_weights['Verified Badge Trust'] = -40

    # Clamp score to 0..100
    final_score = max(0, min(100, score))

    # Determine risk level
    if final_score < 40:
        risk_level = 'SAFE'
        confidence = 94.0
        recommendation = "Safe profile. Signals align with genuine organic user behavior. Standard browsing caution applies."
    elif final_score < 70:
        risk_level = 'SUSPICIOUS'
        confidence = 91.5
        recommendation = "Suspicious activity detected. Exercise caution before trusting links or messages from this account. Verify through independent channels."
    else:
        risk_level = 'HIGH_RISK'
        confidence = 95.8
        recommendation = "High risk assessment. Multiple deceptive indicators detected. Do not click links, send funds, or disclose credentials. Report and block profile."

    if not reasons:
        reasons.append("Account metrics match standard organic user baselines.")

    return {
        'risk_score': final_score,
        'risk_level': risk_level,
        'confidence': confidence,
        'reasons': reasons,
        'factor_weights': factor_weights,
        'recommendation': recommendation,
        'raw_features': feat,
    }
