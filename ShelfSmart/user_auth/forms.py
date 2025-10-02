from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


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


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")
    contact = forms.CharField(required=True, label="Contact Number", max_length=50)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "contact": "Contact No",
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

        # Contact field is declared directly on the form, update its attrs separately
        self.fields["contact"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": placeholders["contact"],
            }
        )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"contact": self.cleaned_data["contact"]},
            )
        return user
