from django.contrib import admin, auth

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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


admin.site.unregister(auth.models.Group)
