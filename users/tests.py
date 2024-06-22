import copy
import random
from http import HTTPStatus

from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase

from users.device_choices import DeviceChoices
from users.models import User


class UserTests(APITestCase):
    def setUp(self):
        User.objects.all().delete()

    def get_correct_phone_number(self):
        return "7" + str(random.randint(1, 9999999999)).zfill(10)

    def get_correct_passport_number(self):
        return f"{str(random.randint(1, 9999)).zfill(4)} {str(random.randint(1, 999999)).zfill(6)}"

    def check_cases(self, url: str, cases: list[tuple[dict, dict, int, str]]):
        total_objects = 0
        for case in cases:
            with self.subTest():
                response = self.client.post(url, data=case[1], headers=case[0], format="json")
                self.assertEqual(response.status_code, case[2], case[3])
                if case[2] == HTTPStatus.CREATED:
                    total_objects += 1
                self.assertEqual(User.objects.count(), total_objects)

    def test_create_user_mobile(self):
        """
        Ensure we can create a new user object with mobile header.
        """
        url = reverse("users:create_user")
        mobile_create_cases = []

        correct_headers = {"x-Device": DeviceChoices.MOBILE}
        incorrect_headers = {"x-Device": "some_text"}

        correct_data = {"phone": self.get_correct_phone_number()}

        mobile_create_cases.append(
            (
                correct_headers,
                correct_data,
                HTTPStatus.CREATED,
                f"Не создается учетная запись при корректных данных, {correct_data.get('phone')}",
            )
        )
        incorrect_header_data = {"phone": self.get_correct_phone_number()}
        mobile_create_cases.append(
            (
                incorrect_headers,
                incorrect_header_data,
                HTTPStatus.BAD_REQUEST,
                "Создается учетная запись при некорректном заголовке",
            )
        )
        empty_header_data = {"phone": self.get_correct_phone_number()}
        mobile_create_cases.append(
            ({}, empty_header_data, HTTPStatus.BAD_REQUEST, "Создается учетная запись при пустом заголовке")
        )
        # Проверка кастомной валидации полей
        right_passport_data = {
            "phone": self.get_correct_phone_number(),
            "passport_number": self.get_correct_passport_number(),
        }
        mobile_create_cases.append(
            (
                correct_headers,
                right_passport_data,
                HTTPStatus.CREATED,
                "Не создается учетная запись при корректном номере паспорта",
            )
        )
        for passport_number in [
            "111 111111",
            "1111 11111",
            "11111 111111",
            "1111 1111111",
            "1111111111",
            "111a 111111",
            "1111 11111a",
            ["1111 1111111"],
        ]:
            incorrect_passport_data = {"phone": self.get_correct_phone_number(), "passport_number": passport_number}
            mobile_create_cases.append(
                (
                    correct_headers,
                    incorrect_passport_data,
                    HTTPStatus.BAD_REQUEST,
                    "Создается учетная запись при некорректном номере паспорта",
                )
            )
        for phone_number in [
            "89111111111",
            "7911111111",
            "791111111111",
            "70000000000",
            "7911111111a",
            "7911111111,",
            ["79111111111"],
        ]:
            wrong_phone_data = {"phone": phone_number}
            mobile_create_cases.append(
                (
                    correct_headers,
                    wrong_phone_data,
                    HTTPStatus.BAD_REQUEST,
                    "Создается учетная запись при некорректном номере телефона",
                )
            )
        self.check_cases(url, mobile_create_cases)

    def test_create_user_mail(self):
        fake = Faker()
        url = reverse("users:create_user")
        mail_create_cases = []

        correct_headers = {"x-Device": DeviceChoices.MAIL}

        correct_data = {
            "email": fake.email(),
            "first_name": fake.first_name(),
        }

        mail_create_cases.append(
            (correct_headers, correct_data, HTTPStatus.CREATED, "Не создается учетная запись при корректных данных")
        )
        # Проверка заполнения полей
        for data in (
            {"email": fake.email(), "first_name": ""},
            {"email": fake.email(), "first_name": [fake.first_name()]},
            {"email": "", "first_name": fake.first_name()},
            {"email": [fake.email()], "first_name": fake.first_name()},
            {"email": "", "first_name": ""},
        ):
            mail_create_cases.append(
                (correct_headers, data, HTTPStatus.BAD_REQUEST, "Создается учетная запись при некорректных данных")
            )

        self.check_cases(url, mail_create_cases)

    def test_create_user_web(self):
        fake = Faker()
        url = reverse("users:create_user")
        web_create_cases = []

        correct_headers = {"x-Device": DeviceChoices.WEB}

        correct_data = {
            "phone": self.get_correct_phone_number(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "patronymic": fake.first_name(),
            "passport_number": self.get_correct_passport_number(),
            "birth_place": fake.address(),
            "register_address": fake.address(),
            "birth_date": fake.date(),
        }

        web_create_cases.append(
            (correct_headers, correct_data, HTTPStatus.CREATED, "Не создается учетная запись при корректных данных")
        )
        for field in correct_data.keys():
            incorrect_data = copy.deepcopy(correct_data)
            del incorrect_data[field]
            if field != "phone":
                incorrect_data["phone"] = self.get_correct_phone_number()
            web_create_cases.append(
                (
                    correct_headers,
                    incorrect_data,
                    HTTPStatus.BAD_REQUEST,
                    "Создается учетная запись при некорректных данных",
                )
            )
        self.check_cases(url, web_create_cases)

    def test_retrieve_user(self):
        fake, user, data = self.create_user()
        url = reverse("users:detail_user", kwargs={"pk": user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK, "Нет доступа к пользователю")
        self.assertEqual(User.objects.count(), 1, "Ошибка создания пользователя")
        self.assertEqual(response.data, data, "Возвращаются некорректные данные")

    def test_users_list(self):
        fake, user, data = self.create_user()
        for i in range(10):
            User.objects.create(
                phone=self.get_correct_phone_number(),
                passport_number=self.get_correct_passport_number(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                patronymic=fake.first_name(),
                birth_date=fake.date(),
                register_address=fake.address(),
                birth_place=fake.address(),
                residence_address=fake.address(),
            )
        url = reverse("users:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK, "Нет доступа к списку пользователей")
        self.assertTrue(data in response.data, "Некорректно выводится пользователь")
        for key in ("email", "first_name", "last_name", "patronymic", "phone"):
            new_url = url + f"?{key}={data.get(key)}"
            response = self.client.get(new_url)
            self.assertEqual(response.status_code, HTTPStatus.OK, "Нет доступа к списку пользователей")
            self.assertTrue(data in response.data, "Некорректно выводится пользователь при фильтрации")

    def create_user(self):
        fake = Faker()
        phone = self.get_correct_phone_number()
        passport = self.get_correct_passport_number()
        email = fake.email()
        first_name = fake.first_name()
        last_name = fake.last_name()
        patronymic = fake.first_name()
        birth_date = fake.date()
        register_address = fake.address()
        birth_place = fake.address()
        residence_address = fake.address()
        user = User.objects.create(
            phone=phone,
            passport_number=passport,
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            birth_date=birth_date,
            register_address=register_address,
            birth_place=birth_place,
            residence_address=residence_address,
        )
        data = {
            "phone": phone,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "birth_date": birth_date,
            "register_address": register_address,
            "birth_place": birth_place,
            "residence_address": residence_address,
            "passport_number": passport,
            "id": user.id,
        }
        return fake, user, data
