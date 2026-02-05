from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress
from django import forms
from django.utils.translation import gettext_lazy as _


class SystolaSignupForm(SignupForm):
    def clean_email(self):
        email = super().clean_email()
        if EmailAddress.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("Этот email уже зарегистрирован. Пожалуйста, войдите в аккаунт.")
            )
        return email
