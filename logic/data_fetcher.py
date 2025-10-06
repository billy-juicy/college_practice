from logic.db_utils import get_connection

def get_partners():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, type, rating, legal_address, inn, director_name, phone, email, logo_url FROM partners")
    data = cur.fetchall()
    conn.close()
    return data

def get_partner_service_history(partner_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name, os.quantity, os.expected_date
        FROM orders o
        JOIN order_services os ON o.id = os.order_id
        JOIN services s ON s.id = os.service_id
        WHERE o.partner_id = ?
        ORDER BY os.expected_date DESC
    """, (partner_id,))
    data = cur.fetchall()
    conn.close()
    return data
