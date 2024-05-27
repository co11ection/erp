from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=8,
        max_length=20,
        required=True,
        write_only=True,
        help_text="Пароль должен содержать от 8 до 20 символов.",
    )
    telegram_username = serializers.CharField(required=False)
    telegram_id = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)
    
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
            "telegram_username",
            "telegram_id",
            "date_of_birth"
        )

    def create(self, validated_data):
        password = validated_data["password"]
        user = User(**validated_data)
        user.set_password(password)
        user.create_activation_code()
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, required=True)
    new_password = serializers.CharField(min_length=8, required=True)
    new_password_confirm = serializers.CharField(min_length=8, required=True)

    def validate_old_password(self, old_password):
        request = self.context.get("request")
        user = request.user
        if not user.check_password(old_password):
            raise serializers.ValidationError("Введите корректный пороль")
        return old_password

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")
        if new_password != new_password_confirm:
            raise serializers.ValidationError("Пороли не совпадают")
        if new_password == old_password:
            raise serializers.ValidationError("Старый и новый пороль совпадают")
        return attrs

    def set_new_password(self):
        new_password = self.validated_data.get("new_password")
        user = self.context.get("request").user
        user.set_password(new_password)
        user.save()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = "password"


class GetAllUserSerializer(serializers.ModelSerializer):
    average_result = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "average_result",
        )
