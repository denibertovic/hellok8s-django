from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField


UserModel = get_user_model()


class MyUserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the
    required fields, plus a repeated password.
    """

    class Meta:
        model = UserModel
        fields = ("email", "first_name", "last_name")

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password Confirmation", widget=forms.PasswordInput
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(MyUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class MyUserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields
    on the user, but replaces the password field with
    admin"s password hash display field.
    """

    class Meta:
        model = UserModel
        fields = ("password",)

    password = ReadOnlyPasswordHashField(
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        )
    )

    def clean_password(self):
        # Regardless of what the user provides, return the
        # initial value. This is done here, rather than on
        # the field, because the field does not have access
        # to the initial value
        return self.initial["password"]
