from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            msg = "Users must have an email"
            raise ValueError(msg)

        user = self.model(
            email=MyUserManager.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email
        and password.
        """
        user = self.create_user(
            email=email, first_name=first_name, last_name=last_name, password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    """
    Inherits from both the AbstractBaseUser and
    PermissionMixin.
    """

    email = models.EmailField(max_length=255, db_index=True, unique=True, blank=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = MyUserManager()

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        try:
            return "{0} {1}".format(self.first_name, self.last_name)
        except Exception:
            return self.email

    def __str__(self):
        return self.get_short_name()

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])
