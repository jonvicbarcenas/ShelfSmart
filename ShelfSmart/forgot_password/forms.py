from django import forms
from django.contrib.auth import get_user_model

from .models import PasswordResetOTP


UserModel = get_user_model()


class UsernameResetForm(forms.Form):
    username = forms.CharField(max_length=150, strip=True)
    otp = forms.CharField(max_length=PasswordResetOTP._meta.get_field("code").max_length, strip=True)
    new_password1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    new_password2 = forms.CharField(min_length=8, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = None
        self._otp_instance = None

        input_attrs = {
            "class": "password-input",
            "required": True,
        }

        self.fields["username"].widget.attrs.update(
            {
                **input_attrs,
                "placeholder": "Username",
                "id": "username",
                "autocomplete": "username",
                "autofocus": True,
            }
        )
        password_attrs = {
            **input_attrs,
            "autocomplete": "new-password",
            "minlength": 8,
        }
        self.fields["otp"].widget.attrs.update(
            {
                **input_attrs,
                "placeholder": "OTP Code",
                "id": "otpCode",
                "autocomplete": "one-time-code",
                "maxlength": PasswordResetOTP._meta.get_field("code").max_length,
                "inputmode": "numeric",
            }
        )

        password_attrs = {
            **input_attrs,
            "autocomplete": "new-password",
            "minlength": 8,
        }
        self.fields["new_password1"].widget.attrs.update(
            {
                **password_attrs,
                "placeholder": "New Password",
                "id": "newPassword",
            }
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                **password_attrs,
                "placeholder": "Confirm Password",
                "id": "confirmPassword",
            }
        )

        for field in self.fields.values():
            field.help_text = None

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        try:
            self._user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            raise forms.ValidationError("No account found with that username.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        otp_code = cleaned_data.get("otp")

        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "Passwords do not match.")

        if self._user and otp_code and not self.errors.get("otp"):
            try:
                self._otp_instance = PasswordResetOTP.objects.validate_otp(self._user, otp_code)
            except PasswordResetOTP.DoesNotExist:
                self.add_error("otp", "Invalid OTP code. Please request a new one.")
            except PasswordResetOTP.Expired:
                self.add_error("otp", "OTP has expired. Please request a new one.")

        return cleaned_data

    def save(self):
        if not hasattr(self, "_user") or self._user is None:
            raise ValueError("Cannot reset password without a valid user.")

        user = self._user
        user.set_password(self.cleaned_data["new_password1"])
        user.save()

        otp_instance = getattr(self, "_otp_instance", None)
        if otp_instance:
            otp_instance.mark_as_used()

        return user
