from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class LoginForm(AuthenticationForm):
    """Custom login form that applies consistent styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Username",
                "autofocus": True,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Password",
            }
        )
        for field in self.fields.values():
            field.help_text = None


UserModel = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")
    phone = forms.CharField(required=False, label="Phone Number", max_length=15)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "phone",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "phone": "Phone Number (Optional)",
            "email": "Email",
            "username": "Username",
            "password1": "Password",
            "password2": "Confirm Password",
        }
        for name, field in self.fields.items():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs.update(
                {
                    "class": f"{css_classes} form-input".strip(),
                    "placeholder": placeholders.get(name, field.label),
                }
            )
            field.help_text = None

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if self._meta.model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone = self.cleaned_data.get("phone", "")
        # Set default values for new fields
        user.user_type = 'user'  # Default to 'user' as specified
        user.status = 'active'   # Default to 'active' as specified
        if commit:
            user.save()
        return user
