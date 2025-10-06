import sqlite3
import math
from logic.db_utils import get_connection

def calculate_material_quantity(service_id: int, material_id: int,
                                service_count: int, *service_params: float) -> int:
    if service_count <= 0 or any(p <= 0 for p in service_params):
        return -1

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT estimated_cost FROM services WHERE id = ?", (service_id,))
        s = cur.fetchone()
        if not s:
            return -1
        service_coeff = s[0] or 1.0

        cur.execute("SELECT cost FROM materials WHERE id = ?", (material_id,))
        m = cur.fetchone()
        if not m:
            return -1
        overuse = m[0] / 100

        base = math.prod(service_params) * service_coeff
        total = base * service_count * (1 + overuse)
        return math.ceil(total)
    except Exception:
        return -1
    finally:
        conn.close()
