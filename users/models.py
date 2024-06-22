from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField("Имя", max_length=64, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=64, blank=True, null=True)
    patronymic = models.CharField("Отчество", max_length=64, blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    phone = models.CharField("Номер телефона", max_length=16, blank=True, null=True)
    passport_number = models.CharField("номер паспорта", max_length=16, blank=True, null=True)
    birth_place = models.CharField("Место рождения", max_length=1024, blank=True, null=True)
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    register_address = models.CharField("Адрес регистрации", max_length=1024, blank=True, null=True)
    residence_address = models.CharField("Адрес проживания", max_length=1024, blank=True, null=True)
    username = models.CharField("Ник пользователя", unique=True, max_length=128)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.email:
                self.username = self.email
            elif self.phone:
                self.username = self.phone
        super().save(*args, **kwargs)
