from django.urls import path

from users.views import CreateUserAPIView, ListUserAPIView, RetrieveUserAPIView

app_name = "users"

urlpatterns = [
    path("list/", ListUserAPIView.as_view(), name="list"),
    path("create/", CreateUserAPIView.as_view(), name="create_user"),
    path("detail/<pk>/", RetrieveUserAPIView.as_view(), name="detail_user"),
]
