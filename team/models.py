from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Team(models.Model):
    """팀 모델

    Args:
        team_name (CharField): 팀 이름
    """

    team_name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.team_name)


class User(AbstractBaseUser):
    """유저 모델

    Args:
        email (EmailField): 이메일(아이디)
        team (ForeignKey): 팀모델 외래키
        username (CharField): 유저이름
        is_active (BooleanField): 활성화 여부
        is_admin (BooleanField): 관리자 여부

    """

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
