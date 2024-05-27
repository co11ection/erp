from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework import status
from django.db.models import Count, F, functions, Case, When, Value, FloatField

from .serializers import (
    RegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    GetAllUserSerializer,
)
from .permissions import CanAccessUsersAndRoles
from config.tasks import send_email_code_task

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            if user:
                try:
                    send_email_code_task.delay(user.email, user.activation_code)
                except:
                    return Response(
                        {
                            "msg": "Зарегистрировано но проблема с отправкой подтверждения",
                            "data": serializer.data,
                        },
                        status=201,
                    )
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ActivationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ""
            user.save()
            html_content = render_to_string("users/activation_success.html")
            return HttpResponse(html_content)
        except Exception:
            html_content = render_to_string("users/activation_error.html")
            return HttpResponse(html_content, status=400)


class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response({"msg": "Пароль успешно обновлен"}, status=200)


class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllUserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = GetAllUserSerializer
    permission_classes = [CanAccessUsersAndRoles]
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        queryset = (
            self.get_queryset()
            .annotate(
                total_reports=Count("reports"),
                all_users_total_reports=Count("reports", distinct=True),
            )
            .annotate(
                average_result=Case(
                    When(all_users_total_reports=0, then=Value(0)),
                    default=functions.Round(
                        F("total_reports") / F("all_users_total_reports") * 100, 2
                    ),
                    output_field=FloatField(),
                )
            )
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
