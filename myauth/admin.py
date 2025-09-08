from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.adapter import get_adapter

from .models import MyUser


class MyUserAdmin(UserAdmin):
    """Custom user admin for email-based authentication."""

    # The fields to be used in displaying the User model
    list_display = (
        "email",
        "is_staff",
        "first_name",
        "last_name",
        "email_verified",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    actions = ["resend_verification_email"]

    def email_verified(self, obj):
        """Display email verification status."""
        try:
            email_address = EmailAddress.objects.get(user=obj, email=obj.email)
            return email_address.verified
        except EmailAddress.DoesNotExist:
            return False

    email_verified.boolean = True
    email_verified.short_description = "Email Verified"

    def resend_verification_email(self, request, queryset):
        """Admin action to resend verification emails for selected users."""
        success_count = 0
        error_count = 0

        for user in queryset:
            try:
                # Get or create EmailAddress record
                email_address, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=user.email,
                    defaults={"verified": False, "primary": True},
                )

                # Skip if already verified
                if email_address.verified:
                    messages.warning(
                        request, f"Email {user.email} is already verified - skipped"
                    )
                    continue

                # Get or create email confirmation (reuse existing if email sending failed)
                email_confirmation = EmailConfirmation.objects.filter(
                    email_address=email_address
                ).first()

                if not email_confirmation:
                    # Create new confirmation if none exists
                    email_confirmation = EmailConfirmation.create(email_address)
                    email_confirmation.save()

                # Send verification email using adapter (works for both new and existing confirmations)
                adapter = get_adapter()
                adapter.send_confirmation_mail(
                    request, email_confirmation, signup=False
                )

                success_count += 1

            except Exception as e:
                error_count += 1
                messages.error(
                    request,
                    f"Failed to send verification email to {user.email}: {str(e)}",
                )

        if success_count > 0:
            messages.success(
                request,
                f"Successfully sent verification emails to {success_count} user(s)",
            )

        if error_count > 0:
            messages.error(
                request,
                f"Failed to send {error_count} verification email(s) - see individual error messages above",
            )

    resend_verification_email.short_description = (
        "Resend verification email to selected users"
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("date_joined",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


admin.site.register(MyUser, MyUserAdmin)
