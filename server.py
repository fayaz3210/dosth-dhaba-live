import os
import json
import sqlite3
import urllib.parse
import urllib.request
import threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer

# ============================================================
# DOSTH DHABA - BACKEND SERVER
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "dd_orders.db")

def send_admin_notification(order_id, table_no, customer_name, customer_mobile, total_amount, items):
    def _send():
        try:
            topic = os.environ.get("NTFY_TOPIC", "dosth_dhaba_orders_alert")
            ntfy_url = f"https://ntfy.sh/{topic}"
            msg = f"Table/Hut: {table_no}\nGuest: {customer_name} ({customer_mobile})\nTotal: Rs.{total_amount}\n\nItems:\n"
            for item in items:
                portion_str = f" ({item['portion']})" if item.get('portion') else ""
                msg += f"- {item.get('qty', 1)}x {item.get('name', 'Item')}{portion_str} -> Rs.{item.get('price', 0) * item.get('qty', 1)}\n"
            
            headers = {
                "Title": f"🔔 New Order #{order_id} - {table_no}",
                "Priority": "urgent",
                "Tags": "bell,curry"
            }
            app_url = os.environ.get("APP_URL", "")
            if app_url:
                headers["Click"] = f"{app_url.rstrip('/')}/admin.html"

            req = urllib.request.Request(
                ntfy_url,
                data=msg.encode('utf-8'),
                headers=headers
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as err:
            print("Notification error:", err)

    threading.Thread(target=_send, daemon=True).start()

# ============================================================
# DATABASE
# ============================================================

def init_db():
    os.makedirs(BASE_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_no TEXT NOT NULL,
            customer_name TEXT,
            customer_mobile TEXT,
            items_json TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            item_name TEXT PRIMARY KEY,
            is_available INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# MENU DATA
# ============================================================

MENU_DATA = [

    # --------------------------------------------------------
    # MUTTON
    # --------------------------------------------------------

    {
        "category_id": "mutton",
        "category_name": "🥩 Mutton Curry",
        "icon": "🥩",
        "items": [
            {"name": "Mutton Fry", "price": 280, "type": "nonveg"},
            {"name": "Mutton Pepper Fry", "price": 290, "type": "nonveg"},
            {"name": "Mutton Chukka", "price": 290, "type": "nonveg"},
            {"name": "Mughlai Mutton", "price": 280, "type": "nonveg"},
            {"name": "Mutton Curry", "price": 280, "type": "nonveg"},
            {"name": "Pepper Mutton Curry", "price": 290, "type": "nonveg"},
            {"name": "Afgani Mutton", "price": 300, "type": "nonveg"},
            {"name": "Kadai Mutton", "price": 290, "type": "nonveg"},
            {"name": "Andhra Mutton", "price": 280, "type": "nonveg"},
            {"name": "Punjabi Mutton", "price": 300, "type": "nonveg"},
            {"name": "D.D Mutton Special", "price": 320, "type": "nonveg"},
            {"name": "Mutton Malai", "price": 300, "type": "nonveg"},
            {"name": "Garlic Mutton", "price": 290, "type": "nonveg"},
            {"name": "Chettinad Mutton", "price": 290, "type": "nonveg"},
            {"name": "Kaju Mutton", "price": 330, "type": "nonveg"}
        ]
    },

    # --------------------------------------------------------
    # ROTTI
    # --------------------------------------------------------

    {
        "category_id": "rotti",
        "category_name": "🫓 Rotti Items",
        "icon": "🫓",
        "items": [
            {"name": "Phulka", "price": 10, "type": "veg"},
            {"name": "DB. Phulka", "price": 15, "type": "veg"},
            {"name": "T. Rotti", "price": 15, "type": "veg"},
            {"name": "P. Naan", "price": 60, "type": "veg"},
            {"name": "B. Naan (Butter Naan)", "price": 70, "type": "veg"},
            {"name": "G.P Naan", "price": 70, "type": "veg"},
            {"name": "G.B Naan", "price": 80, "type": "veg"},
            {"name": "Pudina Naan", "price": 70, "type": "veg"},
            {"name": "G. Rotti", "price": 30, "type": "veg"},
            {"name": "G.B. Rotti", "price": 35, "type": "veg"},
            {"name": "Paneer Kulcha", "price": 80, "type": "veg"},
            {"name": "Onion Kulcha", "price": 90, "type": "veg"},
            {"name": "Chicken Kulcha", "price": 110, "type": "nonveg"}
        ]
    },

    # --------------------------------------------------------
    # VEG FRIED RICE
    # --------------------------------------------------------

    {
        "category_id": "veg-rice",
        "category_name": "🍚 Veg Fried Rice",
        "icon": "🍚",
        "items": [
            {"name": "Veg Rice", "price": 100, "type": "veg"},
            {"name": "Paneer Rice", "price": 150, "type": "veg"},
            {"name": "Gobi Rice", "price": 130, "type": "veg"},
            {"name": "Mushroom Rice", "price": 160, "type": "veg"},
            {"name": "Kaju Rice", "price": 200, "type": "veg"},
            {"name": "Channa Rice", "price": 120, "type": "veg"},
            {"name": "Jeera Rice", "price": 120, "type": "veg"},
            {"name": "Mix Veg Rice", "price": 200, "type": "veg"}
        ]
    },

    # --------------------------------------------------------
    # NON VEG FRIED RICE
    # --------------------------------------------------------

    {
        "category_id": "nonveg-rice",
        "category_name": "🍗 Non-Veg Fried Rice",
        "icon": "🍗",
        "items": [
            {"name": "Chicken Rice", "price": 130, "type": "nonveg"},
            {"name": "Mutton Rice", "price": 210, "type": "nonveg"},
            {"name": "Prawn Rice", "price": 190, "type": "nonveg"},
            {"name": "Dhaba Rice", "price": 150, "type": "nonveg"},
            {"name": "Mix Non-Veg Rice", "price": 250, "type": "nonveg"}
        ]
    },

    # --------------------------------------------------------
    # VEG CURRY
    # --------------------------------------------------------

    {
        "category_id": "veg-curry",
        "category_name": "🥘 Veg Curry",
        "icon": "🥘",
        "items": [
            {"name": "Dal Fry", "price": 100, "type": "veg"},
            {"name": "Dal Tadka", "price": 120, "type": "veg"},
            {"name": "Dal Makhani", "price": 140, "type": "veg"},
            {"name": "Channa Masala", "price": 120, "type": "veg"},
            {"name": "Mix Veg Curry", "price": 180, "type": "veg"},
            {"name": "Kadai Paneer", "price": 190, "type": "veg"},
            {"name": "Paneer Butter Masala", "price": 190, "type": "veg"},
            {"name": "Andhra Paneer", "price": 190, "type": "veg"},
            {"name": "Kaju Curry", "price": 230, "type": "veg"},
            {"name": "Kaju Tomato Curry", "price": 230, "type": "veg"},
            {"name": "Kaju Paneer", "price": 240, "type": "veg"},
            {"name": "Gobi Curry", "price": 130, "type": "veg"},
            {"name": "Mushroom Curry", "price": 160, "type": "veg"},
            {"name": "Kadai Mushroom", "price": 180, "type": "veg"},
            {"name": "Kadai Kaju Paneer", "price": 230, "type": "veg"},
            {"name": "Garlic Paneer", "price": 180, "type": "veg"},
            {"name": "Chettinad Paneer", "price": 190, "type": "veg"},
            {"name": "Punjabi Paneer", "price": 200, "type": "veg"}
        ]
    },

    # --------------------------------------------------------
    # NON VEG CURRY
    # --------------------------------------------------------

    {
        "category_id": "nonveg-curry",
        "category_name": "🍲 Non-Veg Curry",
        "icon": "🍲",
        "items": [
            {
                "name": "Mix Non-Veg Curry",
                "portions": {"Bone": 270, "Boneless": 300},
                "type": "nonveg"
            },
            {
                "name": "Chicken Muhali",
                "portions": {"Bone": 220, "Boneless": 250},
                "type": "nonveg"
            },
            {
                "name": "Chicken Curry",
                "portions": {"Bone": 150, "Boneless": 180},
                "type": "nonveg"
            },
            {
                "name": "Butter Chicken",
                "portions": {"Bone": 220, "Boneless": 250},
                "type": "nonveg"
            },
            {
                "name": "Kadai Chicken",
                "portions": {"Bone": 220, "Boneless": 250},
                "type": "nonveg"
            },
            {
                "name": "Hyderabadi Chicken",
                "portions": {"Bone": 250, "Boneless": 280},
                "type": "nonveg"
            },
            {
                "name": "Rambha Chicken",
                "portions": {"Bone": 250, "Boneless": 280},
                "type": "nonveg"
            },
            {
                "name": "Punjabi Chicken",
                "portions": {"Bone": 250, "Boneless": 280},
                "type": "nonveg"
            },
            {
                "name": "D.D Chicken Special",
                "portions": {"Bone": 290, "Boneless": 350},
                "type": "nonveg"
            },
            {
                "name": "Kaju Chicken",
                "portions": {"Bone": 250, "Boneless": 280},
                "type": "nonveg"
            },
            {
                "name": "Chettinadu Chicken",
                "portions": {"Bone": 220, "Boneless": 250},
                "type": "nonveg"
            },
            {
                "name": "Pepper Chicken",
                "portions": {"Bone": 170, "Boneless": 200},
                "type": "nonveg"
            },
            {
                "name": "Kashmiri Chicken",
                "portions": {"Bone": 220, "Boneless": 250},
                "type": "nonveg"
            },
            {
                "name": "Garlic Chicken",
                "portions": {"Bone": 220, "Boneless": 250},
                "type": "nonveg"
            },
            {"name": "Ginger Chicken", "price": 120, "type": "nonveg"},
            {"name": "Anda Keema", "price": 120, "type": "nonveg"},
            {"name": "Anda Curry", "price": 140, "type": "nonveg"},
            {
                "name": "Raja Rani",
                "portions": {"Bone": 280, "Boneless": 310},
                "type": "nonveg"
            }
        ]
    },

    # --------------------------------------------------------
    # VEG STARTER
    # --------------------------------------------------------

    {
        "category_id": "veg-starter",
        "category_name": "🧆 Veg Starter",
        "icon": "🧆",
        "items": [
            {"name": "Paneer Chilly", "price": 180, "type": "veg"},
            {"name": "Paneer 65", "price": 200, "type": "veg"},
            {"name": "Mushroom 65", "price": 170, "type": "veg"},
            {"name": "Mushroom Chilly", "price": 180, "type": "veg"},
            {"name": "Paneer Manchurian", "price": 180, "type": "veg"},
            {"name": "Mushroom Manchurian", "price": 170, "type": "veg"},
            {"name": "Pepper Paneer Fry", "price": 170, "type": "veg"},
            {"name": "Gobi 65", "price": 140, "type": "veg"},
            {"name": "Gobi Chilly", "price": 160, "type": "veg"},
            {"name": "Gobi Manchurian", "price": 160, "type": "veg"},
            {"name": "Kari Roast", "price": 200, "type": "veg"},
            {"name": "Channa Roast", "price": 140, "type": "veg"}
        ]
    },

    # --------------------------------------------------------
    # NON VEG STARTER
    # --------------------------------------------------------

    {
        "category_id": "nonveg-starter",
        "category_name": "🍤 Non-Veg Starter",
        "icon": "🍤",
        "items": [
            {"name": "Chicken 65", "price": 170, "type": "nonveg"},
            {"name": "Chicken Manchurian", "price": 170, "type": "nonveg"},
            {"name": "Chicken Lollipop (6 Pcs)", "price": 220, "type": "nonveg"},
            {"name": "Chicken Chilly", "price": 210, "type": "nonveg"},
            {"name": "Chicken Wings (6 Pcs)", "price": 180, "type": "nonveg"},
            {"name": "Prawn Chilly", "price": 230, "type": "nonveg"},
            {"name": "Prawn Manchurian", "price": 220, "type": "nonveg"},
            {"name": "Prawn Pepper Fry", "price": 210, "type": "nonveg"},
            {"name": "Prawn Pepper Roast", "price": 210, "type": "nonveg"},
            {"name": "Pepper Chicken Roast", "price": 200, "type": "nonveg"},
            {"name": "Fish Finger", "price": 200, "type": "nonveg"}
        ]
    },

    # --------------------------------------------------------
    # TANDOORI
    # --------------------------------------------------------

    {
        "category_id": "tandoori",
        "category_name": "🍢 Tandoori Items",
        "icon": "🍢",
        "items": [
            {
                "name": "Tandoori Chicken",
                "portions": {
                    "Full": 480,
                    "Half": 250,
                    "Quarter": 130
                },
                "type": "nonveg"
            },
            {
                "name": "Grill Chicken",
                "portions": {
                    "Full": 500,
                    "Half": 260,
                    "Quarter": 140
                },
                "type": "nonveg"
            }
        ]
    },

    # --------------------------------------------------------
    # TIKKA
    # --------------------------------------------------------

    {
        "category_id": "tikka",
        "category_name": "🔥 Tikka Items",
        "icon": "🔥",
        "items": [
            {"name": "Creme Tikka", "price": 250, "type": "nonveg"},
            {"name": "Mint Tikka", "price": 230, "type": "nonveg"},
            {"name": "Thava Tikka", "price": 220, "type": "nonveg"}
        ]
    }
]


# ============================================================
# JSON RESPONSE HELPER
# ============================================================

def send_json(handler, data, status=200):

    response = json.dumps(
        data,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(status)

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )

    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type"
    )

    handler.send_header(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, OPTIONS"
    )

    handler.send_header(
        "Content-Length",
        str(len(response))
    )

    handler.end_headers()

    handler.wfile.write(response)


# ============================================================
# REQUEST HANDLER
# ============================================================

class RequestHandler(SimpleHTTPRequestHandler):

    def address_string(self):
        # Disable slow reverse DNS lookups for instant response speed
        return self.client_address[0]

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=BASE_DIR,
            **kwargs
        )

    # --------------------------------------------------------
    # OPTIONS
    # --------------------------------------------------------

    def do_OPTIONS(self):

        send_json(
            self,
            {"success": True}
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def do_GET(self):

        parsed = urllib.parse.urlparse(self.path)

        # ----------------------------------------------------
        # ROUTE ALIASES
        # ----------------------------------------------------
        if parsed.path in ["/admin", "/admin/"]:
            self.path = "/admin.html"
            return super().do_GET()

        # ----------------------------------------------------
        # MENU API
        # ----------------------------------------------------

        if parsed.path == "/api/menu":

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT item_name, is_available FROM stock"
            )

            stock_map = {
                row[0]: bool(row[1])
                for row in cursor.fetchall()
            }

            conn.close()

            menu_copy = json.loads(
                json.dumps(MENU_DATA)
            )

            for category in menu_copy:

                for item in category["items"]:

                    item["is_available"] = stock_map.get(
                        item["name"],
                        True
                    )

            send_json(
                self,
                {
                    "success": True,
                    "menu": menu_copy
                }
            )

            return

        # ----------------------------------------------------
        # ORDERS API
        # ----------------------------------------------------

        if parsed.path == "/api/orders":

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    table_no,
                    customer_name,
                    customer_mobile,
                    items_json,
                    total_amount,
                    status,
                    created_at
                FROM orders
                ORDER BY id DESC
                LIMIT 50
            """)

            rows = cursor.fetchall()

            conn.close()

            orders = []

            for row in rows:

                orders.append({
                    "id": row[0],
                    "table_no": row[1],
                    "customer_name": row[2],
                    "customer_mobile": row[3],
                    "items": json.loads(row[4]),
                    "total_amount": row[5],
                    "status": row[6],
                    "created_at": row[7]
                })

            send_json(
                self,
                {
                    "success": True,
                    "orders": orders
                }
            )

            return

        # ----------------------------------------------------
        # NORMAL HTML FILE
        # ----------------------------------------------------

        super().do_GET()

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def do_POST(self):

        parsed = urllib.parse.urlparse(self.path)

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            ).decode("utf-8")

            data = json.loads(body) if body else {}

        except Exception:

            send_json(
                self,
                {
                    "success": False,
                    "message": "Invalid request data."
                },
                400
            )

            return

        # ----------------------------------------------------
        # PLACE ORDER
        # ----------------------------------------------------

        if parsed.path == "/api/order":

            table_no = str(
                data.get(
                    "table_no",
                    ""
                )
            ).strip()

            customer_name = str(
                data.get(
                    "customer_name",
                    "Guest"
                )
            ).strip()

            if not customer_name:
                customer_name = "Guest"

            customer_mobile = str(
                data.get(
                    "customer_mobile",
                    ""
                )
            ).strip()

            items = data.get(
                "items",
                []
            )

            if not table_no:

                send_json(
                    self,
                    {
                        "success": False,
                        "message": "Table number is required."
                    },
                    400
                )

                return

            if not isinstance(items, list) or not items:

                send_json(
                    self,
                    {
                        "success": False,
                        "message": "Cart is empty."
                    },
                    400
                )

                return

            # Calculate total from items
            total_amount = 0

            for item in items:

                try:

                    price = float(
                        item["price"]
                    )

                    qty = int(
                        item["qty"]
                    )

                    total_amount += (
                        price * qty
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError
                ):

                    send_json(
                        self,
                        {
                            "success": False,
                            "message": "Invalid item data."
                        },
                        400
                    )

                    return

            # Save order with current local IST timestamp
            ist_tz = timezone(timedelta(hours=5, minutes=30))
            created_at_str = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO orders
                (
                    table_no,
                    customer_name,
                    customer_mobile,
                    items_json,
                    total_amount,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                table_no,
                customer_name,
                customer_mobile,
                json.dumps(
                    items,
                    ensure_ascii=False
                ),
                total_amount,
                created_at_str
            ))

            order_id = cursor.lastrowid

            conn.commit()
            conn.close()

            # Trigger immediate iPhone / mobile push notification to admin
            send_admin_notification(
                order_id=order_id,
                table_no=table_no,
                customer_name=customer_name,
                customer_mobile=customer_mobile,
                total_amount=total_amount,
                items=items
            )

            send_json(
                self,
                {
                    "success": True,
                    "message": "Order placed!",
                    "order_id": order_id
                }
            )

            return

        # ----------------------------------------------------
        # STOCK API
        # ----------------------------------------------------

        if parsed.path == "/api/stock":

            item_name = str(
                data.get(
                    "item_name",
                    ""
                )
            ).strip()

            if not item_name:

                send_json(
                    self,
                    {
                        "success": False,
                        "message": "Item name is required."
                    },
                    400
                )

                return

            is_available = (
                1
                if data.get(
                    "is_available",
                    True
                )
                else 0
            )

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO stock
                (
                    item_name,
                    is_available
                )
                VALUES (?, ?)
                ON CONFLICT(item_name)
                DO UPDATE SET
                    is_available =
                    excluded.is_available
            """, (
                item_name,
                is_available
            ))

            conn.commit()
            conn.close()

            send_json(
                self,
                {
                    "success": True,
                    "message": "Stock updated."
                }
            )

            return

        send_json(
            self,
            {
                "success": False,
                "message": "API endpoint not found."
            },
            404
        )

    # --------------------------------------------------------
    # PUT - UPDATE ORDER STATUS
    # --------------------------------------------------------

    def do_PUT(self):

        parsed = urllib.parse.urlparse(
            self.path
        )

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            ).decode("utf-8")

            data = json.loads(
                body
            ) if body else {}

        except Exception:

            send_json(
                self,
                {
                    "success": False,
                    "message": "Invalid request data."
                },
                400
            )

            return

        if parsed.path.startswith(
            "/api/order/"
        ):

            try:

                order_id = int(
                    parsed.path
                    .rstrip("/")
                    .split("/")[-1]
                )

            except ValueError:

                send_json(
                    self,
                    {
                        "success": False,
                        "message": "Invalid order ID."
                    },
                    400
                )

                return

            new_status = str(
                data.get(
                    "status",
                    "Pending"
                )
            )

            allowed_statuses = {
                "Pending",
                "Preparing",
                "Ready",
                "Completed",
                "Cancelled"
            }

            if new_status not in allowed_statuses:

                send_json(
                    self,
                    {
                        "success": False,
                        "message": "Invalid status."
                    },
                    400
                )

                return

            conn = sqlite3.connect(
                DB_FILE
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE orders
                SET status = ?
                WHERE id = ?
                """,
                (
                    new_status,
                    order_id
                )
            )

            updated = cursor.rowcount

            conn.commit()
            conn.close()

            if not updated:

                send_json(
                    self,
                    {
                        "success": False,
                        "message": "Order not found."
                    },
                    404
                )

                return

            send_json(
                self,
                {
                    "success": True,
                    "message": "Status updated."
                }
            )

            return

        send_json(
            self,
            {
                "success": False,
                "message": "API endpoint not found."
            },
            404
        )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        RequestHandler
    )

    print()
    print("==============================================")
    print("       DOSTH DHABA ORDERING SYSTEM")
    print("==============================================")
    print()
    print("Server is running.")
    print()
    print("Open this in your browser:")
    print("http://localhost:8000")
    print()
    print("Press CTRL + C to stop the server.")
    print("==============================================")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("Server stopped.")

        server.server_close()