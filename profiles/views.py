from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from .utils import change_photo
from loguru import logger
import logging
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from .models import UserProfile, UserMedal
from .serializers import (
    UserProfileSerializer,
    UserProfileListSerializer,
    ChangePasswordSerializer,
    UserProfileEditSerializer,
)
from home_page.utils import get_data_user
from users.permissions import (
    CanViewUserProfile,
    CanAccessUsersAndRoles,
    CanChangePasswordUserProfile,
    CanViewWorkSchedule,
)
from periods.models import Periods
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated, CanViewUserProfile])
def view_profile(request):
    """
    Просмотр профиля пользователя.

    Получает и возвращает информацию о профиле зарегистрированного пользователя,
    включая имя и фамилию.

    Поля:
     user - email пользователя
    telegram_id - тг id пользователя
    telegram_username - тг username
    last_sync_date - дата последней синхронизации
    notification_time - время оповещения (час, минута, секунда)
    notification_frequency  - (daily, weekly, monthly)
    days_without_skip
    medals

    Returns:
        Response: Ответ с данными профиля пользователя.
    """
    user_profile = UserProfile.objects.get(user=request.user)
    serializer = UserProfileSerializer(user_profile)
    user_data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    profile_data = serializer.data
    profile_data.update(user_data)

    return Response(profile_data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, CanAccessUsersAndRoles])
def edit_profile(request):
    try:
        user = User.objects.get(email=request.data.get("email"))
        user_profile = UserProfile.objects.get(user=user)
        serializer = UserProfileEditSerializer(user_profile, data=request.data)

        # Update user role and permissions
        role = request.data.get("role")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        middle_name = request.data.get("middle_name")
        is_active = request.data.get("is_active")

        if role:
            user.role = role

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        if middle_name:
            user.middle_name = middle_name

        if is_active:
            user.is_active = is_active

        user.category_metrics_permission = request.data.get(
            "category_metrics_permission", False
        )
        user.create_reports_permission = request.data.get(
            "create_reports_permission", False
        )
        user.period_permission = request.data.get("period_permission", False)
        user.statistick_permission = request.data.get("statistick_permission", False)
        user.metrics_permission = request.data.get("metrics_permission", False)
        user.users_and_roles_permission = request.data.get(
            "users_and_roles_permission", False
        )
        user.reports_permission = request.data.get("reports_permission", False)
        user.save()

        if serializer.is_valid():
            # Respond with user profile data
            return Response(
                {"user_profile": serializer.data}, status=status.HTTP_200_OK
            )

        return Response(
            {
                "user_profile": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as ex:
        logging.error(f"An error occurred: {ex}")
        return Response(
            {"error": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, CanAccessUsersAndRoles])
def change_role(request):
    try:
        email = request.data.get("email")
        role = request.data.get("role")
        user = User.objects.filter(email=email).first()
        user_profile = UserProfile.objects.get(user=user)
        serializer = UserProfileEditSerializer(user_profile, data=request.data)
        user = user_profile.user
        if serializer.is_valid():
            if role:
                user.role = role
                user.save()
            serializer.save()
            return Response(serializer.data)

    except Exception as ex:
        return Response(
            {"error": f"Something goes wrong: {ex}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_profile_photo(request):
    """
    Обновить фото пользователя.
    parameters:
        description: Base64-encoded image string.

    responses:
      200:
        description: User photo updated successfully.
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        values = request.data
        change_photo(user_profile, values.get("photo"))

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status.HTTP_200_OK)

    except Exception as ex:
        return Response(
            {"error": f"Something goes wrong: {ex}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, CanChangePasswordUserProfile])
def change_password(request):
    """
    Изменение пароля пользователя.

    Методы:
    -post(request) - изменение пороль пользователей

    Поля:
    email
    current_password
    new_password
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        if not request.user.check_password(
            serializer.validated_data["current_password"]
        ):
            return Response(
                {"current_password": ["Неверный текущий пароль."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response(
            {"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([CanAccessUsersAndRoles])
def get_all_person(request):
    """
    Получение списка всех пользователей.

    Пример запроса:
    GET /api/all-person/
    """
    users = UserProfile.objects.all()
    serializer = UserProfileListSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_medal(request):
    user_profile = request.user.userprofile

    medal_name = request.data.get("medal_name")

    if medal_name:
        medal = UserMedal.objects.get(name=medal_name)
        user_profile.medals.add(medal)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "medal_name is required"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    id = request.query_params.get("id")

    user_profile = get_object_or_404(UserProfile, id=id)

    user_details = {
        "first_name": user_profile.user.first_name,
        "last_name": user_profile.user.last_name,
        "middle_name": user_profile.user.middle_name,
        "is_active": user_profile.user.is_active,
    }

    serializer = UserProfileEditSerializer(user_profile).data
    serializer.update(user_details)
    return Response(serializer, status=status.HTTP_200_OK)


from rest_framework import generics
from .models import Schedule
from .serializers import ScheduleSerializer


class ScheduleBulkCreateView(generics.CreateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = request.query_params.get("id")
        user = UserProfile.objects.get(pk=user_id)

        schedules = []
        for date, is_working in data.items():
            existing_schedule = self.queryset.filter(user=user.pk, date=date)
            if existing_schedule:
                return Response("Данные уже созданы", status=400)
            schedules.append({"user": user.pk, "date": date, "is_working": is_working})

        serializer = self.get_serializer(data=schedules, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ScheduleBulkDeleteView(generics.DestroyAPIView):
    logger.info("start")
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def destroy(self, request, *args, **kwargs):
        data = request.data.get("dates")
        user_id = request.query_params.get("id")
        user = UserProfile.objects.get(pk=user_id)
        logger.info(f"user: {user}")

        deleted_schedules = False

        for date in data:
            schedule = self.queryset.filter(user=user.pk, date=date).first()
            logger.info(f"schedule: {schedule}")
            if schedule:
                schedule.delete()
                deleted_schedules = True
                logger.info(f"schedule del: {schedule}")

        if deleted_schedules:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                data="No schedules to delete", status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_result(request):
    email = request.query_params.get("email")
    period_id = request.query_params.get("id")
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    selected_period = get_object_or_404(
            Periods, start_date=start_date, end_date=end_date, id=period_id
        )
    user = User.objects.get(email=email)
    user_profile = UserProfile.objects.get(user=user)
    result = get_data_user(user=user, user_profile=user_profile, selected_period=selected_period)
    return Response(result)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_birthday(request):
    date_of_birth = request.data.get("date_of_birth")
    user = User.objects.get(email=request.user)
    user.date_of_birth = date_of_birth
    user.save()
    return Response({"data": "changed"})