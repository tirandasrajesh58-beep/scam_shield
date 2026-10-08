from django import forms

class ProfileAnalysisForm(forms.Form):
    """
    Input form for social media profile risk assessment.
    """
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'e.g. elon_crypto_giveaway992'
        })
    )
    display_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'e.g. Elon Musk (Official Giveaway)'
        })
    )
    followers = forms.IntegerField(
        min_value=0,
        initial=10,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary'
        })
    )
    following = forms.IntegerField(
        min_value=0,
        initial=2500,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary'
        })
    )
    posts = forms.IntegerField(
        min_value=0,
        initial=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary'
        })
    )
    account_age_days = forms.IntegerField(
        min_value=0,
        initial=3,
        required=True,
        label="Account Age (Days)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'rows': 3,
            'placeholder': 'e.g. DM on Telegram @official_bonus to claim ₹50,000 cash reward!'
        })
    )
    external_link = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'e.g. https://bit.ly/free-bonus-claim'
        })
    )
    is_verified = forms.BooleanField(
        required=False,
        label="Verified Badge",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    has_profile_pic = forms.BooleanField(
        required=False,
        initial=True,
        label="Has Profile Image",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
