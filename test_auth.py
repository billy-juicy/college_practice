import unittest
from logic.auth import authenticate_user


class TestAuthenticateUser(unittest.TestCase):

    def test_empty_fields(self):
        """Негативный тест — пустые поля"""
        result = authenticate_user("", "")
        self.assertEqual(result, "EMPTY_FIELDS")

    def test_user_not_found(self):
        """Негативный тест — несуществующий пользователь"""
        result = authenticate_user("no_user@example.com", "12345")
        self.assertEqual(result, "NOT_FOUND")

    def test_wrong_password(self):
        """Негативный тест — неверный пароль"""
        # замените на существующий email из базы
        result = authenticate_user("sidorov@cleanplanet.ru", "wrongpass")
        self.assertEqual(result, "WRONG_PASSWORD")

    def test_admin_login(self):
        """Позитивный тест — корректный вход администратора"""
        result = authenticate_user("sidorov@cleanplanet.ru", "adminpass")
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[2], "admin")

    def test_partner_login(self):
        """Позитивный тест — корректный вход партнёра"""
        result = authenticate_user("greenplanet@example.com", "part234")
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[2], "partner")


if __name__ == "__main__":
    unittest.main()
