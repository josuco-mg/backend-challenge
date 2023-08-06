from pydantic import ValidationError
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from account.services import services
from account.services import unit_of_work
from common.utils import parsed_validation_error
from web.accounts import permissions


class UserCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated & permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            user_id = services.create_user(
                username=request.data["username"],
                password=request.data["password"],
                is_admin=request.data.get("is_admin", False),
                uow=unit_of_work.DjangoUserUnitOfWork(),
            )
        except services.UsernameAlreadyExists as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                parsed_validation_error(e), status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"id": user_id}, status=status.HTTP_201_CREATED)
