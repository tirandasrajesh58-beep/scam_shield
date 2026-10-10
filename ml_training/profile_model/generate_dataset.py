"""
Dataset Generator for Social Media Profile Risk Analysis.
Synthesizes a realistic 1,200-sample research benchmark dataset with natural noise
and distribution overlap (mimicking real-world Twitter/Instagram bot behaviors).
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

def generate_profile_dataset(num_samples=1200, output_path=None):
    num_genuine = num_samples // 2
    num_fake = num_samples - num_genuine

    # --- Genuine Profiles (600 samples) ---
    followers_gen = np.random.exponential(scale=2000, size=num_genuine) + 40
    following_gen = np.random.exponential(scale=450, size=num_genuine) + 15
    posts_gen = np.random.exponential(scale=500, size=num_genuine) + 10
    age_gen = np.random.uniform(low=90, high=3200, size=num_genuine)

    # Inject 6% noisy genuine users: new users or casual users with few posts/followers
    noise_gen_idx = np.random.choice(num_genuine, size=int(0.06 * num_genuine), replace=False)
    followers_gen[noise_gen_idx] = np.random.uniform(5, 50, size=len(noise_gen_idx))
    following_gen[noise_gen_idx] = np.random.uniform(200, 1200, size=len(noise_gen_idx))
    posts_gen[noise_gen_idx] = np.random.choice([0, 1, 2], size=len(noise_gen_idx))
    age_gen[noise_gen_idx] = np.random.uniform(5, 45, size=len(noise_gen_idx))

    is_verified_gen = np.random.choice([0, 1], size=num_genuine, p=[0.92, 0.08])
    has_pic_gen = np.random.choice([0, 1], size=num_genuine, p=[0.05, 0.95])
    has_bio_gen = np.random.choice([0, 1], size=num_genuine, p=[0.10, 0.90])
    has_link_gen = np.random.choice([0, 1], size=num_genuine, p=[0.65, 0.35])
    digits_ratio_gen = np.random.beta(a=1.5, b=6, size=num_genuine)

    df_genuine = pd.DataFrame({
        'followers': np.maximum(0, followers_gen).astype(int),
        'following': np.maximum(0, following_gen).astype(int),
        'posts': np.maximum(0, posts_gen).astype(int),
        'account_age_days': np.maximum(1, age_gen).astype(int),
        'is_verified': is_verified_gen,
        'has_profile_pic': has_pic_gen,
        'has_bio': has_bio_gen,
        'has_external_link': has_link_gen,
        'digits_ratio': np.round(digits_ratio_gen, 3),
        'is_fake': 0
    })

    # --- Fake / Bot Profiles (600 samples) ---
    followers_fake = np.random.exponential(scale=60, size=num_fake) + 3
    following_fake = np.random.uniform(low=800, high=5500, size=num_fake)
    posts_fake = np.random.choice([0, 1, 2, 3, 5, 12], size=num_fake, p=[0.30, 0.25, 0.15, 0.15, 0.10, 0.05])
    age_fake = np.random.uniform(low=1, high=70, size=num_fake)

    # Inject 6% sophisticated/purchased bots (have higher followers or older age)
    noise_fake_idx = np.random.choice(num_fake, size=int(0.06 * num_fake), replace=False)
    followers_fake[noise_fake_idx] = np.random.uniform(1500, 8000, size=len(noise_fake_idx))
    following_fake[noise_fake_idx] = np.random.uniform(300, 1500, size=len(noise_fake_idx))
    age_fake[noise_fake_idx] = np.random.uniform(200, 1000, size=len(noise_fake_idx))

    is_verified_fake = np.zeros(num_fake, dtype=int)
    has_pic_fake = np.random.choice([0, 1], size=num_fake, p=[0.38, 0.62])
    has_bio_fake = np.random.choice([0, 1], size=num_fake, p=[0.45, 0.55])
    has_link_fake = np.random.choice([0, 1], size=num_fake, p=[0.25, 0.75])
    digits_ratio_fake = np.random.beta(a=3, b=2.5, size=num_fake)

    df_fake = pd.DataFrame({
        'followers': np.maximum(0, followers_fake).astype(int),
        'following': np.maximum(0, following_fake).astype(int),
        'posts': np.maximum(0, posts_fake).astype(int),
        'account_age_days': np.maximum(1, age_fake).astype(int),
        'is_verified': is_verified_fake,
        'has_profile_pic': has_pic_fake,
        'has_bio': has_bio_fake,
        'has_external_link': has_link_fake,
        'digits_ratio': np.round(digits_ratio_fake, 3),
        'is_fake': 1
    })

    # Combine & Shuffle
    df = pd.concat([df_genuine, df_fake], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Derived Features
    df['following_follower_ratio'] = np.round(df['following'] / (df['followers'] + 1), 3)
    df['posts_per_day'] = np.round(df['posts'] / np.maximum(df['account_age_days'], 1), 3)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} samples saved to: {output_path}")

    return df

if __name__ == '__main__':
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'social_profiles_dataset.csv'))
    generate_profile_dataset(1200, dataset_path)
