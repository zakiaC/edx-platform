from django import forms
from django.contrib.auth import get_user_model

try:
    from django.contrib.auth.forms import AdminUserCreationForm as _BaseForm
except ImportError:
    from django.contrib.auth.forms import UserCreationForm as _BaseForm


class MissionAdminUserCreationForm(_BaseForm):
    """
    Enforce a non-empty email on Django admin user creation.
    This avoids DB IntegrityError with unique auth_user.email.
    """

    email = forms.EmailField(required=True, label="Adresse email")

    class Meta(_BaseForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        value = (self.cleaned_data.get("email") or "").strip().lower()
        if not value:
            raise forms.ValidationError("L'adresse email est obligatoire.")
        return value
