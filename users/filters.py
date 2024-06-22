from django_filters import rest_framework as filters

from users.models import User


class UserFilter(filters.FilterSet):
    """
    Фильтрация списка пользователей
    """

    first_name = filters.CharFilter(method="filter_first_name", label="Фильтр по имени")
    last_name = filters.CharFilter(method="filter_last_name", label="Фильтр по фамилии")
    patronymic = filters.CharFilter(method="filter_patronymic", label="Фильтр по отчеству")
    email = filters.CharFilter(method="email_filter", label="Фильтр по email")
    phone = filters.CharFilter(method="phone_filter", label="Фильтр по телефону")

    class Meta:
        model = User
        distinct = True
        fields = ("first_name", "last_name", "patronymic", "email", "phone")

    @staticmethod
    def filter_first_name(queryset, _, value):
        if value:
            queryset = queryset.filter(first_name__icontains=value)
        return queryset

    @staticmethod
    def filter_last_name(queryset, _, value):
        if value:
            queryset = queryset.filter(last_name__icontains=value)
        return queryset

    @staticmethod
    def filter_patronymic(queryset, _, value):
        if value:
            queryset = queryset.filter(patronymic__icontains=value)
        return queryset

    @staticmethod
    def email_filter(queryset, _, value):
        if value:
            queryset = queryset.filter(email__icontains=value)
        return queryset

    @staticmethod
    def phone_filter(queryset, _, value):
        if value:
            queryset = queryset.filter(phone__icontains=value)
        return queryset
