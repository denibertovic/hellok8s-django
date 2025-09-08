from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from myutils.helpers import has_spam_trigger_in_text, has_tld_domain_in_text
from django_cf_turnstile.fields import TurnstileCaptchaField
from allauth.account.forms import LoginForm as BaseLogin
from allauth.account.forms import SignupForm as BaseSignup
from allauth.account.forms import ResetPasswordForm as BaseReset

User = get_user_model()


class LoginForm(BaseLogin):
    captcha = TurnstileCaptchaField(label="")


class SignupForm(BaseSignup):
    captcha = TurnstileCaptchaField(label="")


class ResetPasswordForm(BaseReset):
    captcha = TurnstileCaptchaField(label="")


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "block w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "block w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500",
                    "placeholder": "Last name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "block w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500",
                    "placeholder": "Email address",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email field readonly since allauth handles email changes
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["email"].help_text = "To change your email, please contact support."

    def clean_first_name(self):
        """Validate first name for spam content."""
        first_name = self.cleaned_data.get("first_name")
        if first_name and (
            has_spam_trigger_in_text(first_name) or has_tld_domain_in_text(first_name)
        ):
            raise ValidationError("Names cannot contain URLs or domain names.")
        return first_name

    def clean_last_name(self):
        """Validate last name for spam content."""
        last_name = self.cleaned_data.get("last_name")
        if last_name and (
            has_spam_trigger_in_text(last_name) or has_tld_domain_in_text(last_name)
        ):
            raise ValidationError("Names cannot contain URLs or domain names.")
        return last_name
