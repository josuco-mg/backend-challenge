from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from account.domain import model as domain_model


CAN_CREATE_USERS_CODENAME = "can_create_users"
CAN_CREATE_USERS_PERM = f"accounts.{CAN_CREATE_USERS_CODENAME}"


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str, is_admin: bool) -> "User":
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        if is_admin:
            can_create_users_perm = Permission.objects.get(
                codename=CAN_CREATE_USERS_CODENAME,
                content_type=ContentType.objects.get_for_model(self.model),
            )
            user.user_permissions.add(can_create_users_perm)
        return user

    def create_superuser(
        self, username: str, password: str, **extra_fields
    ) -> "User":
        return self.create_user(username, password, is_admin=True)


class User(AbstractUser):
    objects = UserManager()

    class Meta:
        permissions = [(CAN_CREATE_USERS_CODENAME, "Can create users")]

    @property
    def is_admin(self):
        return self.has_perm(CAN_CREATE_USERS_PERM)

    def to_domain(self) -> domain_model.User:
        return domain_model.User(
            id=self.id,
            username=self.username,
            is_admin=self.is_admin,
        )
