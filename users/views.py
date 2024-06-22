from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions

from users.filters import UserFilter
from users.models import User
from users.serializers import UserCreateSerializer, UserFullSerializer


class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    # не оговорено, но необходимо ограничить возможность создания пользователей
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["device"] = self.request.META.get("HTTP_X_DEVICE")
        return context


class RetrieveUserAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserFullSerializer


class ListUserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserFullSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter
