import hashlib
from logic.db_utils import get_connection


def authenticate_user(email: str, password: str):
    """
    Проверяет существование пользователя и корректность пароля.
    Возвращает:
        - кортеж (id, full_name, role, partner_id) при успешной авторизации;
        - строку ошибки ("EMPTY_FIELDS", "NOT_FOUND", "WRONG_PASSWORD").
    """
    if not email or not password:
        return "EMPTY_FIELDS"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, full_name, role, password FROM employees WHERE email=?", (email,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return "NOT_FOUND"

    hashed = hashlib.sha256(password.encode()).hexdigest()
    if user[3] != hashed:
        conn.close()
        return "WRONG_PASSWORD"

    # Если роль partner, ищем partner_id
    partner_id = None
    if user[2].lower() == "partner":
        cur.execute("SELECT id FROM partners WHERE email=?", (email,))
        res = cur.fetchone()
        if res:
            partner_id = res[0]

    conn.close()
    return (user[0], user[1], user[2].lower(), partner_id)
