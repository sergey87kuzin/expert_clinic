import re

from django.db.models import Q
from rest_framework import serializers

from users.device_choices import DeviceChoices
from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "phone",
            "passport_number",
            "birth_date",
            "birth_place",
            "register_address",
            "residence_address",
        )

    def validate(self, attrs):  # noqa
        device = self.context.get("device")
        if not device or device not in DeviceChoices.ALL_DEVICES:
            raise serializers.ValidationError("Устройство не передано или передано некорректно")
        if device == DeviceChoices.MOBILE:
            if not attrs.get("phone"):
                raise serializers.ValidationError({"phone": "Поле phone обязательно"})
        elif device == DeviceChoices.MAIL:
            if not attrs.get("email"):
                raise serializers.ValidationError({"email": "Поле email обязательно"})
            if not attrs.get("first_name"):
                raise serializers.ValidationError({"first_name": "Поле first_name обязательно"})
        elif device == DeviceChoices.WEB:
            exclude_fields = ("email", "residence_address")
            for field_name in self.Meta.fields:
                if field_name not in exclude_fields:
                    if not attrs.get(field_name):
                        raise serializers.ValidationError({field_name: f"Поле {field_name} обязательно"})
        return attrs

    def validate_phone(self, value):
        if value:
            if User.objects.filter(Q(phone=value) | Q(username=value)).exists():
                raise serializers.ValidationError(
                    {"phone": "Пользователь с таким номером телефона уже зарегистрирован"}
                )
            pattern = re.compile("^7([0-9]{10})")
            if not pattern.fullmatch(value) or value == "70000000000":
                raise serializers.ValidationError({"phone": "Неверный формат ввода номера. Нужен 7xxxxxxxxxx"})
        return value

    def validate_email(self, value):
        if value:
            if User.objects.filter(Q(email=value) | Q(username=value)).exists():
                raise serializers.ValidationError({"email": "Пользователь с таким email уже зарегистрирован"})
        return value

    def validate_passport_number(self, value):
        if value:
            pattern = re.compile("^[0-9]{4} [0-9]{6}$")
            if not pattern.fullmatch(value):
                raise serializers.ValidationError({"passport_number": "Неверный формат. Нужен xxxx xxxxxx"})
        return value


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "phone",
            "passport_number",
            "birth_date",
            "birth_place",
            "register_address",
            "residence_address",
        )
