from django.utils.functional import cached_property

from pydantic import ValidationError
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from account.domain import model as account_model
from account.services import services as account_services
from common.utils import parsed_validation_error
from ecg.adapters import repository
from ecg.services import services as ecg_services
from ecg.services import unit_of_work
from web.accounts import permissions
from web.ecgs import tasks


class ECGViewMixin:
    permission_classes = [IsAuthenticated & ~permissions.IsAdminUser]

    @cached_property
    def user(self) -> account_model.User:
        return account_services.get_user_by_username(
            username=self.request.user.username
        )


class ECGCreateView(ECGViewMixin, generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            ecg_id = ecg_services.create_ecg(
                creator=self.user,
                lead_results=request.data["lead_results"],
                uow=unit_of_work.DjangoECGUnitOfWork(),
            )
        except ValidationError as e:
            return Response(
                parsed_validation_error(e), status=status.HTTP_400_BAD_REQUEST
            )

        tasks.task_process_ecg.delay(ecg_id=ecg_id)
        return Response({"id": ecg_id}, status=status.HTTP_201_CREATED)


class ECGStatsView(ECGViewMixin, generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        ecg = ecg_services.get_ecg_by_id(
            id=kwargs["pk"], ecgs=repository.DjangoECGRepository()
        )
        if not ecg or ecg.creator.id != self.user.id:
            return Response(
                {"message": "Not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not ecg.is_processed:
            return Response(
                {"message": "Still processing"}, status=status.HTTP_409_CONFLICT
            )

        return Response(ecg.stats_model_dump(), status=status.HTTP_200_OK)
