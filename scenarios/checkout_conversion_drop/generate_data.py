#!/usr/bin/env python3
"""
Generate all realistic scenario data files for SimWork's "checkout_conversion_drop" scenario.

Scenario: FoodDash food delivery platform. Weekly orders dropped 18% over the past month.
Root cause: PayStream v3 payment gateway migration on Jan 10, 2025 introduced latency
regression affecting iOS disproportionately.
"""

import csv
import os
import random
import hashlib
from datetime import datetime, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TABLES_DIR = os.path.join(SCRIPT_DIR, "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# Date range
START_DATE = datetime(2024, 12, 15)
END_DATE = datetime(2025, 1, 31, 23, 59, 59)
MIGRATION_DATE = datetime(2025, 1, 10)

PLATFORMS = ["ios", "android", "web"]
REGIONS = ["us_east", "us_west", "eu", "asia"]
USER_TYPES = ["new", "returning", "power", "casual"]

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster",
]

CUISINE_TYPES = ["italian", "chinese", "indian", "mexican", "american", "thai", "japanese", "pizza", "burgers", "sushi"]

RESTAURANT_NAMES = {
    "italian": ["Bella Italia", "Trattoria Roma", "Pasta Palace", "Olive Garden Express", "La Dolce Vita"],
    "chinese": ["Dragon Palace", "Golden Wok", "Jade Garden", "Lucky Star Chinese", "Bamboo Kitchen"],
    "indian": ["Spice Route", "Curry House", "Taj Mahal Kitchen", "Mumbai Bites", "Saffron Indian"],
    "mexican": ["El Sombrero", "Taco Fiesta", "Casa de Burrito", "La Cantina", "Aztec Grill"],
    "american": ["Liberty Diner", "Eagle Grill", "Main Street Eats", "Classic American", "Blue Plate Special"],
    "thai": ["Thai Orchid", "Bangkok Kitchen", "Pad Thai Express", "Lotus Thai", "Siam Garden"],
    "japanese": ["Sakura Kitchen", "Tokyo Ramen House", "Zen Japanese", "Samurai Grill", "Nippon Bento"],
    "pizza": ["Pizza Planet", "Slice of Heaven", "Napoli Pizza", "The Pizza Box", "Crust & Co"],
    "burgers": ["Burger Barn", "The Patty Shack", "Flame Grill Burgers", "Stack House", "Bun & Done"],
    "sushi": ["Sushi Master", "Rolling Fish", "Ocean Roll", "Fresh Catch Sushi", "Blue Fin Sushi"],
}

MENU_ITEMS_BY_CUISINE = {
    "italian": [
        ("Margherita Pizza", "Classic tomato sauce, mozzarella, and basil", 14),
        ("Spaghetti Carbonara", "Creamy pasta with pancetta and parmesan", 16),
        ("Chicken Parmigiana", "Breaded chicken with marinara and cheese", 18),
        ("Fettuccine Alfredo", "Creamy garlic parmesan pasta", 15),
        ("Bruschetta", "Toasted bread with tomatoes, garlic, and basil", 10),
        ("Tiramisu", "Classic Italian coffee dessert", 9),
        ("Lasagna", "Layered pasta with meat sauce and ricotta", 17),
        ("Risotto Mushroom", "Creamy arborio rice with wild mushrooms", 16),
    ],
    "chinese": [
        ("Kung Pao Chicken", "Spicy stir-fried chicken with peanuts", 15),
        ("Sweet and Sour Pork", "Crispy pork in tangy sauce", 14),
        ("Beef Chow Mein", "Stir-fried noodles with beef and vegetables", 13),
        ("Spring Rolls", "Crispy vegetable rolls with dipping sauce", 9),
        ("Mapo Tofu", "Spicy tofu in Sichuan sauce", 12),
        ("Fried Rice", "Wok-fried rice with egg and vegetables", 11),
        ("Dim Sum Platter", "Assorted steamed dumplings", 16),
    ],
    "indian": [
        ("Butter Chicken", "Tender chicken in creamy tomato sauce", 16),
        ("Lamb Vindaloo", "Spicy lamb curry with potatoes", 18),
        ("Palak Paneer", "Spinach and cottage cheese curry", 14),
        ("Chicken Biryani", "Fragrant rice with spiced chicken", 15),
        ("Naan Bread", "Traditional tandoor-baked flatbread", 8),
        ("Samosa", "Crispy pastry with spiced potato filling", 9),
        ("Tikka Masala", "Grilled chicken in spiced masala sauce", 17),
    ],
    "mexican": [
        ("Chicken Burrito", "Flour tortilla with chicken, rice, and beans", 13),
        ("Beef Tacos", "Three corn tortillas with seasoned beef", 12),
        ("Quesadilla", "Grilled tortilla with cheese and chicken", 11),
        ("Nachos Supreme", "Loaded nachos with all the fixings", 14),
        ("Enchiladas", "Rolled tortillas in red sauce with cheese", 15),
        ("Guacamole & Chips", "Fresh avocado dip with tortilla chips", 10),
    ],
    "american": [
        ("Classic Cheeseburger", "Angus beef patty with cheddar and fixings", 14),
        ("BBQ Ribs", "Slow-smoked pork ribs with BBQ sauce", 22),
        ("Grilled Chicken Sandwich", "Herb-marinated chicken breast sandwich", 13),
        ("Caesar Salad", "Romaine lettuce with croutons and parmesan", 12),
        ("Mac and Cheese", "Creamy baked macaroni and cheese", 11),
        ("Philly Cheesesteak", "Sliced beef with melted cheese on hoagie", 15),
        ("Apple Pie", "Classic American apple pie with ice cream", 9),
    ],
    "thai": [
        ("Pad Thai", "Stir-fried rice noodles with shrimp", 14),
        ("Green Curry", "Coconut green curry with chicken", 15),
        ("Tom Yum Soup", "Spicy and sour shrimp soup", 12),
        ("Mango Sticky Rice", "Sweet coconut rice with fresh mango", 10),
        ("Thai Fried Rice", "Wok-fried jasmine rice with basil", 13),
        ("Satay Skewers", "Grilled chicken with peanut sauce", 11),
    ],
    "japanese": [
        ("Teriyaki Chicken", "Grilled chicken with teriyaki glaze", 15),
        ("Tonkotsu Ramen", "Rich pork bone broth ramen", 16),
        ("Gyoza", "Pan-fried pork dumplings", 10),
        ("Katsu Curry", "Breaded pork cutlet with Japanese curry", 17),
        ("Edamame", "Steamed soybeans with sea salt", 8),
        ("Tempura Udon", "Thick noodles with shrimp tempura", 14),
    ],
    "pizza": [
        ("Pepperoni Pizza", "Classic pepperoni with mozzarella", 15),
        ("Hawaiian Pizza", "Ham and pineapple pizza", 14),
        ("Veggie Supreme", "Loaded vegetable pizza", 16),
        ("BBQ Chicken Pizza", "Chicken with BBQ sauce and red onion", 17),
        ("Garlic Bread", "Toasted bread with garlic butter", 8),
        ("Buffalo Wings", "Spicy chicken wings with ranch", 12),
    ],
    "burgers": [
        ("Double Stack Burger", "Two beef patties with cheese and sauce", 16),
        ("Mushroom Swiss Burger", "Beef patty with mushrooms and Swiss", 15),
        ("Crispy Chicken Burger", "Breaded chicken with spicy mayo", 14),
        ("Veggie Burger", "Plant-based patty with avocado", 13),
        ("Loaded Fries", "Fries with cheese, bacon, and sour cream", 10),
        ("Onion Rings", "Beer-battered onion rings", 9),
        ("Milkshake", "Thick vanilla or chocolate shake", 8),
    ],
    "sushi": [
        ("California Roll", "Crab, avocado, and cucumber roll", 12),
        ("Salmon Nigiri", "Fresh salmon over seasoned rice", 14),
        ("Spicy Tuna Roll", "Tuna with spicy mayo and tempura flakes", 13),
        ("Dragon Roll", "Eel, cucumber, topped with avocado", 16),
        ("Sashimi Platter", "Assorted fresh raw fish", 22),
        ("Miso Soup", "Traditional soybean soup", 8),
        ("Edamame", "Steamed soybeans with sea salt", 8),
    ],
}

IOS_DEVICES = ["iPhone 14", "iPhone 14 Pro", "iPhone 15", "iPhone 15 Pro", "iPhone SE"]
ANDROID_DEVICES = ["Pixel 7", "Pixel 7 Pro", "Samsung S23", "Samsung S23 Ultra", "Samsung A54"]
WEB_DEVICES = ["Chrome", "Safari", "Firefox", "Edge"]

ADDRESSES = [
    "123 Main St", "456 Oak Ave", "789 Elm Blvd", "321 Pine Dr", "654 Maple Ln",
    "111 Broadway", "222 Market St", "333 Park Ave", "444 Lake Rd", "555 River Way",
    "100 First St", "200 Second Ave", "300 Third Blvd", "400 Fourth Dr", "500 Fifth Ln",
]

# ---- Helpers ----

def jitter(val, pct=0.05):
    """Add random jitter of ±pct to a value."""
    return val * (1 + random.uniform(-pct, pct))

def random_datetime(start, end):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)

def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]

def gen_commit_hash():
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:7]

def gen_phone():
    return f"+1{random.randint(200,999)}{random.randint(1000000,9999999)}"

def write_csv(filename, headers, rows):
    path = os.path.join(TABLES_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  -> {filename}: {len(rows)} rows")

def write_md(filename, content):
    path = os.path.join(TABLES_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"  -> {filename}: written")


# ===================== 1. USERS =====================
def generate_users(n=5000):
    print("Generating users.csv...")
    rows = []
    for i in range(1, n + 1):
        uid = f"U{i:05d}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@fooddash.com"
        phone = gen_phone()
        signup = random_datetime(datetime(2023, 1, 1), datetime(2024, 12, 14)).strftime("%Y-%m-%d")
        platform = weighted_choice(PLATFORMS, [45, 35, 20])
        region = weighted_choice(REGIONS, [40, 25, 20, 15])
        utype = weighted_choice(USER_TYPES, [30, 35, 20, 15])
        rows.append([uid, name, email, phone, signup, platform, region, utype])
    write_csv("users.csv", ["user_id", "name", "email", "phone", "signup_date", "platform", "region", "user_type"], rows)
    return rows


# ===================== 2. RESTAURANTS =====================
def generate_restaurants(users):
    print("Generating restaurants.csv...")
    rows = []
    rid = 1
    for cuisine in CUISINE_TYPES:
        names = RESTAURANT_NAMES[cuisine]
        for rname in names:
            rating = round(random.uniform(3.5, 4.9), 1)
            addr = random.choice(ADDRESSES) + f", Suite {random.randint(1,200)}"
            owner = random.choice(users)[0]
            rows.append([f"R{rid:04d}", rname, cuisine, addr, rating, owner])
            rid += 1
    write_csv("restaurants.csv", ["restaurant_id", "name", "cuisine_type", "address", "rating", "owner_id"], rows)
    return rows


# ===================== 3. MENU ITEMS =====================
def generate_menu_items(restaurants):
    print("Generating menu_items.csv...")
    rows = []
    mid = 1
    restaurant_menu_map = {}  # restaurant_id -> list of item_ids
    for rest in restaurants:
        rest_id = rest[0]
        cuisine = rest[2]
        items = MENU_ITEMS_BY_CUISINE.get(cuisine, [])
        n_items = min(len(items), random.randint(4, 8))
        selected = random.sample(items, n_items)
        item_ids = []
        for item_name, desc, base_price in selected:
            price = round(base_price + random.uniform(-2, 5), 2)
            price = max(8.0, min(35.0, price))
            item_id = f"MI{mid:05d}"
            rows.append([item_id, rest_id, item_name, desc, f"{price:.2f}"])
            item_ids.append(item_id)
            mid += 1
        restaurant_menu_map[rest_id] = item_ids
    write_csv("menu_items.csv", ["item_id", "restaurant_id", "name", "description", "price"], rows)
    return rows, restaurant_menu_map


# ===================== 4. ORDERS =====================
def generate_orders(users, restaurants, restaurant_menu_map):
    print("Generating orders.csv...")
    # Build user lookup by platform
    user_by_platform = {"ios": [], "android": [], "web": []}
    user_platform_map = {}
    for u in users:
        user_by_platform[u[5]].append(u[0])
        user_platform_map[u[0]] = u[5]

    rest_ids = [r[0] for r in restaurants]

    orders = []
    oid = 1
    current = START_DATE
    day_num = 0

    while current.date() <= END_DATE.date():
        date = current.date()
        day_of_week = current.weekday()  # 0=Mon, 6=Sun
        is_post_migration = current >= MIGRATION_DATE
        days_after_migration = (current - MIGRATION_DATE).days if is_post_migration else 0

        # Base orders per day
        base = 350
        # Holiday promo bump Dec 26-31
        if datetime(2024, 12, 26).date() <= date <= datetime(2024, 12, 31).date():
            base = 400
        # Post migration: gradual drop
        if is_post_migration:
            drop_factor = 1.0 - (days_after_migration / 21.0) * 0.20  # up to 20% drop over 21 days
            base = int(base * drop_factor)
        # Weekend dip
        if day_of_week in [5, 6]:
            base = int(base * 0.88)
        # Daily noise
        n_orders = max(100, int(jitter(base, 0.05)))

        for _ in range(n_orders):
            # Pick platform with natural distribution, slightly more ios
            plat = weighted_choice(PLATFORMS, [45, 35, 20])
            eligible_users = user_by_platform[plat]
            user_id = random.choice(eligible_users)
            rest_id = random.choice(rest_ids)
            total = round(random.uniform(15, 60), 2)

            # Determine order status
            if is_post_migration:
                if plat == "ios":
                    # iOS failure rate ramps from ~8% to ~35%
                    fail_rate = 0.08 + (days_after_migration / 21.0) * 0.27
                    cancel_rate = 0.15
                elif plat == "android":
                    fail_rate = 0.05 + (days_after_migration / 21.0) * 0.03
                    cancel_rate = 0.15
                else:
                    fail_rate = 0.05 + (days_after_migration / 21.0) * 0.02
                    cancel_rate = 0.15
            else:
                fail_rate = 0.05
                cancel_rate = 0.15

            r = random.random()
            if r < fail_rate:
                status = "failed"
            elif r < fail_rate + cancel_rate:
                status = "cancelled"
            else:
                status = "completed"

            # Random time during the day, weighted toward lunch/dinner
            hour_weights = [1]*6 + [2]*2 + [3]*3 + [2]*2 + [1]*2 + [2]*2 + [3]*3 + [2]*2 + [1]*2
            # hours 0-5: 1, 6-7: 2, 8-10: 3 (not right, let me fix)
            # Better: build explicit hour distribution
            hour = weighted_choice(list(range(24)), [
                1, 1, 1, 1, 1, 1,  # 0-5: very low
                2, 3, 4, 5, 6,     # 6-10: morning ramp
                8, 9, 8, 7,        # 11-14: lunch peak
                4, 3, 3,           # 15-17: afternoon
                8, 9, 8, 7,        # 18-21: dinner peak
                4, 2               # 22-23: late night
            ])
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            created = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=second)

            orders.append([
                f"ORD{oid:06d}", user_id, rest_id, status,
                f"{total:.2f}", plat, created.strftime("%Y-%m-%d %H:%M:%S")
            ])
            oid += 1

        current += timedelta(days=1)
        day_num += 1

    write_csv("orders.csv",
              ["order_id", "user_id", "restaurant_id", "order_status", "total_amount", "platform", "created_at"],
              orders)
    return orders


# ===================== 5. ORDER ITEMS =====================
def generate_order_items(orders, restaurant_menu_map):
    print("Generating order_items.csv...")
    rows = []
    oiid = 1
    for order in orders:
        order_id = order[0]
        rest_id = order[2]
        items_available = restaurant_menu_map.get(rest_id, [])
        if not items_available:
            continue
        n_items = weighted_choice([1, 2, 3, 4], [15, 40, 35, 10])
        selected = random.choices(items_available, k=n_items)
        for item_id in selected:
            qty = weighted_choice([1, 2, 3], [70, 25, 5])
            rows.append([f"OI{oiid:06d}", order_id, item_id, qty])
            oiid += 1
    write_csv("order_items.csv", ["order_item_id", "order_id", "item_id", "quantity"], rows)
    return rows


# ===================== 6. DRIVERS =====================
def generate_drivers(n=200):
    print("Generating drivers.csv...")
    rows = []
    statuses = ["available", "on_delivery", "offline"]
    for i in range(1, n + 1):
        did = f"D{i:04d}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        phone = gen_phone()
        region = weighted_choice(REGIONS, [40, 25, 20, 15])
        status = weighted_choice(statuses, [40, 35, 25])
        rows.append([did, name, phone, region, status])
    write_csv("drivers.csv", ["driver_id", "name", "phone", "region", "availability_status"], rows)
    return rows


# ===================== 7. PAYMENTS =====================
def generate_payments(orders):
    print("Generating payments.csv...")
    rows = []
    pid = 1
    for order in orders:
        order_id = order[0]
        user_id = order[1]
        order_status = order[3]
        total = order[4]
        platform = order[5]
        created_at = order[6]
        order_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        is_post = order_dt >= MIGRATION_DATE
        days_after = (order_dt - MIGRATION_DATE).days if is_post else 0

        # Method
        if platform == "ios":
            method = weighted_choice(["credit_card", "apple_pay", "paypal"], [45, 40, 15])
        elif platform == "android":
            method = weighted_choice(["credit_card", "google_pay", "paypal"], [45, 40, 15])
        else:
            method = weighted_choice(["credit_card", "paypal"], [75, 25])

        # Provider
        provider = "paystream_v3" if is_post else "paystream_v2"

        # Processing time and status
        if not is_post:
            # Baseline
            proc_time = int(jitter(120, 0.35))
            proc_time = max(80, min(200, proc_time))
            r = random.random()
            if r < 0.92:
                status = "success"
                error_code = ""
            elif r < 0.95:
                status = "failed"
                error_code = random.choice(["INSUFFICIENT_FUNDS", "CARD_DECLINED"])
            else:
                status = "timeout"
                error_code = "GATEWAY_TIMEOUT"
        else:
            # Post migration - severity depends on platform
            degradation = min(1.0, days_after / 21.0)  # 0 to 1 over 21 days

            if platform == "ios":
                # Severe degradation
                base_proc = 120 + degradation * 400  # 120 -> 520
                proc_time = int(jitter(base_proc, 0.4))
                if method == "apple_pay":
                    proc_time = int(proc_time * 1.5)  # Apple Pay even worse
                proc_time = max(150, min(4500, proc_time))

                # Success rate drops: 92% -> ~55% (apple_pay -> ~45%)
                success_rate = 0.92 - degradation * 0.37
                if method == "apple_pay":
                    success_rate = 0.92 - degradation * 0.47
                timeout_rate = degradation * 0.30
                fail_rate = 1.0 - success_rate - timeout_rate
                fail_rate = max(0.02, fail_rate)

                r = random.random()
                if r < success_rate:
                    status = "success"
                    error_code = ""
                elif r < success_rate + timeout_rate:
                    status = "timeout"
                    error_code = "GATEWAY_TIMEOUT"
                else:
                    status = "failed"
                    error_code = random.choice(["PAYMENT_PROVIDER_ERROR", "PAYMENT_PROVIDER_ERROR", "GATEWAY_TIMEOUT", "NETWORK_ERROR"])
            elif platform == "android":
                # Mild degradation
                base_proc = 120 + degradation * 50
                proc_time = int(jitter(base_proc, 0.3))
                proc_time = max(100, min(300, proc_time))

                success_rate = 0.92 - degradation * 0.07
                r = random.random()
                if r < success_rate:
                    status = "success"
                    error_code = ""
                elif r < success_rate + 0.03:
                    status = "timeout"
                    error_code = "GATEWAY_TIMEOUT"
                else:
                    status = "failed"
                    error_code = random.choice(["INSUFFICIENT_FUNDS", "CARD_DECLINED", "PAYMENT_PROVIDER_ERROR"])
            else:
                # Web: similar to android
                base_proc = 120 + degradation * 40
                proc_time = int(jitter(base_proc, 0.3))
                proc_time = max(100, min(280, proc_time))

                success_rate = 0.92 - degradation * 0.06
                r = random.random()
                if r < success_rate:
                    status = "success"
                    error_code = ""
                elif r < success_rate + 0.02:
                    status = "timeout"
                    error_code = "GATEWAY_TIMEOUT"
                else:
                    status = "failed"
                    error_code = random.choice(["INSUFFICIENT_FUNDS", "CARD_DECLINED", "PAYMENT_PROVIDER_ERROR"])

        # Align payment status with order status somewhat
        if order_status == "completed" and status != "success":
            # Some completed orders might have had a retry succeed
            if random.random() < 0.7:
                status = "success"
                error_code = ""
                proc_time = max(80, proc_time)
        elif order_status == "failed" and status == "success":
            if random.random() < 0.8:
                status = "failed"
                error_code = random.choice(["GATEWAY_TIMEOUT", "PAYMENT_PROVIDER_ERROR"])

        rows.append([
            f"PAY{pid:06d}", order_id, user_id, method, provider, status,
            total, proc_time, error_code, created_at
        ])
        pid += 1

    write_csv("payments.csv",
              ["payment_id", "order_id", "user_id", "method", "provider", "status",
               "amount", "processing_time_ms", "error_code", "created_at"],
              rows)
    return rows


# ===================== 8. SESSION EVENTS =====================
def generate_session_events(users, orders):
    print("Generating sessions_events.csv...")
    FUNNEL_STEPS = ["app_open", "restaurant_view", "add_to_cart", "checkout_start", "payment_attempt", "order_complete"]

    # Build order lookup by user+date for linking
    rows = []
    eid = 1
    sid = 1

    # Generate ~50,000 events across sessions
    # We'll generate sessions per day
    current = START_DATE
    total_days = (END_DATE - START_DATE).days + 1
    # ~50000 events / 48 days / ~3.3 avg events per session = ~315 sessions/day
    target_sessions_per_day = 315

    while current.date() <= END_DATE.date():
        date = current.date()
        is_post = current >= MIGRATION_DATE
        days_after = (current - MIGRATION_DATE).days if is_post else 0

        # ~230 sessions per day, each producing ~4.5 events on average → ~1035 events/day → ~50K total
        n_sessions = max(150, int(jitter(target_sessions_per_day, 0.08)))

        for _ in range(n_sessions):
            user = random.choice(users)
            user_id = user[0]
            platform = user[5]
            session_id = f"S{sid:07d}"
            sid += 1

            # Device
            if platform == "ios":
                device = random.choice(IOS_DEVICES)
            elif platform == "android":
                device = random.choice(ANDROID_DEVICES)
            else:
                device = random.choice(WEB_DEVICES)

            app_version = "4.2.1" if not is_post else "4.2.2"

            # Session start time, weighted toward lunch/dinner
            hour = weighted_choice(list(range(24)), [
                1, 1, 1, 1, 1, 1,
                2, 3, 4, 5, 6,
                8, 9, 8, 7,
                4, 3, 3,
                8, 9, 8, 7,
                4, 2
            ])
            minute = random.randint(0, 59)
            ts = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=random.randint(0, 59))

            # Baseline funnel probabilities (conditional: probability of continuing to next step)
            # app_open(100%) -> restaurant_view(76%) -> add_to_cart(71%) -> checkout_start(67%) -> payment_attempt(83%) -> order_complete(93%)
            # These compound to: 100, 76, 54, 36, 30, 28
            baseline_probs = [1.0, 0.76, 0.71, 0.67, 0.83, 0.93]

            if is_post and platform == "ios":
                # payment_attempt -> order_complete drops from 93% to ~55%
                degradation = min(1.0, days_after / 21.0)
                completion_rate = 0.93 - degradation * 0.38
                probs = [1.0, 0.76, 0.71, 0.67, 0.83, completion_rate]
            elif is_post and platform == "android":
                degradation = min(1.0, days_after / 21.0)
                completion_rate = 0.93 - degradation * 0.05
                probs = [1.0, 0.76, 0.71, 0.67, 0.83, completion_rate]
            else:
                probs = baseline_probs

            # Walk through funnel
            for step_idx, step in enumerate(FUNNEL_STEPS):
                if step_idx > 0 and random.random() > probs[step_idx]:
                    break
                ts += timedelta(seconds=random.randint(3, 45))
                rows.append([
                    f"E{eid:07d}", user_id, session_id, step, platform, device,
                    app_version, ts.strftime("%Y-%m-%d %H:%M:%S")
                ])
                eid += 1

        current += timedelta(days=1)

    write_csv("sessions_events.csv",
              ["event_id", "user_id", "session_id", "event_type", "platform", "device", "app_version", "timestamp"],
              rows)
    return rows


# ===================== 9. REVIEWS =====================
def generate_reviews(users, orders):
    print("Generating reviews.csv...")
    rows = []
    rid = 1

    # Helper to pick a user/order combo
    def pick_user_order(platform_filter=None, date_start=None, date_end=None):
        candidates = [o for o in orders
                      if (platform_filter is None or o[5] == platform_filter)
                      and (date_start is None or o[6][:10] >= date_start)
                      and (date_end is None or o[6][:10] <= date_end)]
        if candidates:
            o = random.choice(candidates)
            return o[1], o[0], o[5]
        return random.choice(users)[0], "ORD000000", platform_filter or "ios"

    def add_review(uid, oid, rating, text, plat, date_range_start, date_range_end):
        nonlocal rid
        dt = random_datetime(
            datetime.strptime(date_range_start, "%Y-%m-%d"),
            datetime.strptime(date_range_end, "%Y-%m-%d") + timedelta(hours=23, minutes=59)
        )
        rows.append([f"REV{rid:04d}", uid, oid, rating, text, plat, dt.strftime("%Y-%m-%d %H:%M:%S")])
        rid += 1

    # Dec 20 – Jan 9: ~12 reviews, mostly positive
    positive_reviews_early = [
        (5, "Great food delivery! Love how fast it arrived."),
        (4, "Really enjoying the new restaurant filters, makes browsing so much easier."),
        (5, "Fast delivery and the food was still hot. Excellent service!"),
        (4, "Good selection of restaurants. The app is easy to use."),
        (5, "Best delivery app I've used. Always on time."),
        (4, "Nice variety of cuisines. Ordered Thai food and it was great."),
        (5, "Love the app! The tracking feature is super helpful."),
        (3, "Food was good but the search results seem a bit off sometimes. Hard to find specific dishes."),
        (4, "Ordered for a family dinner, everyone was happy with their meals."),
        (5, "Delivery driver was super friendly. Food was perfect."),
        (3, "The new icon design is a bit confusing but otherwise the app works great."),
        (4, "Solid delivery experience. Will order again."),
    ]
    for rating, text in positive_reviews_early:
        uid, oid, plat = pick_user_order(date_start="2024-12-20", date_end="2025-01-09")
        add_review(uid, oid, rating, text, plat, "2024-12-20", "2025-01-09")

    # Jan 10-15: ~8 reviews, first payment complaints
    jan10_15_reviews = [
        ("ios", 1, "Payment keeps failing on my iPhone. Had to try 3 times before it went through."),
        ("ios", 2, "Payment process is really slow now. Waited over a minute for it to process."),
        ("ios", 1, "Can't complete any orders! Payment always times out. Very frustrating."),
        ("android", 4, "Ordered dinner, everything worked smoothly. Great burgers!"),
        ("ios", 2, "Something is wrong with the payment. It just shows 'Something went wrong' every time."),
        ("ios", 1, "Apple Pay hasn't worked for me in days. Had to use my laptop to order."),
        ("ios", 2, "Payment failed twice but worked on the third try. Please fix this!"),
        ("android", 5, "Fast delivery as always. Love the real-time tracking."),
    ]
    for plat, rating, text in jan10_15_reviews:
        uid, oid, _ = pick_user_order(platform_filter=plat, date_start="2025-01-10", date_end="2025-01-15")
        add_review(uid, oid, rating, text, plat, "2025-01-10", "2025-01-15")

    # Jan 16-28: ~30 reviews, flood of payment complaints
    jan16_28_reviews = [
        ("ios", 1, "Payment times out every single time. I've given up trying to order."),
        ("ios", 1, "This app is completely broken. Can't pay for anything on my iPhone."),
        ("ios", 1, "I've switched to UberEats because FoodDash payments never work anymore."),
        ("ios", 1, "Works fine on my husband's Android but my iPhone can't process any payment."),
        ("ios", 1, "Apple Pay is completely broken. Haven't been able to order in 2 weeks."),
        ("ios", 2, "App freezes during payment every time. Have to force close and restart."),
        ("ios", 1, "Payment fails with some generic error message. No explanation, no help."),
        ("ios", 1, "Tried credit card and Apple Pay, neither works. What happened to this app?"),
        ("ios", 2, "Payment takes forever and then fails. Wasted 20 minutes trying to order dinner."),
        ("ios", 1, "Deleted the app. Payment hasn't worked in weeks. Terrible experience."),
        ("ios", 1, "Every order attempt fails at checkout. iPhone 15 Pro, latest iOS."),
        ("ios", 2, "Payment error every time. Error message just says 'Something went wrong'. Not helpful at all."),
        ("ios", 1, "I literally cannot order food anymore. Payment is 100% broken on iOS."),
        ("ios", 1, "Switching to a competitor. Two weeks of broken payments is unacceptable."),
        ("ios", 1, "Asked my coworkers - everyone with an iPhone has this payment issue."),
        ("ios", 2, "Sometimes works after 4-5 tries but usually just times out."),
        ("ios", 1, "Was a loyal customer for 2 years. Now I can't even place an order. Sad."),
        ("ios", 1, "Apple Pay used to be so fast. Now it just spins forever and fails."),
        ("ios", 1, "Got charged twice because the payment timed out but actually went through. Nightmare."),
        ("ios", 2, "The checkout process is painfully slow now. Takes 30+ seconds to process."),
        ("android", 5, "Ordering was smooth! Got my food in 25 minutes. Great experience."),
        ("android", 4, "App works great on my Pixel. Quick checkout, good food."),
        ("android", 4, "No issues at all. Placed 3 orders this week, all perfect."),
        ("ios", 1, "My friend recommended this app but I literally cannot complete a single order."),
        ("ios", 1, "Payment keeps showing gateway timeout. What does that even mean?"),
        ("web", 3, "Delivery was cold when it arrived. Took almost an hour."),
        ("android", 3, "Wrong order received. Got someone else's food. Support was helpful though."),
        ("ios", 1, "Updated the app hoping it would fix payments. Nope, still broken."),
        ("ios", 1, "Three stars? More like zero. Payment system is completely non-functional on iOS."),
        ("ios", 2, "Managed to order once today after 6 attempts. The food was good at least."),
    ]
    for plat, rating, text in jan16_28_reviews:
        uid, oid, _ = pick_user_order(platform_filter=plat, date_start="2025-01-16", date_end="2025-01-28")
        add_review(uid, oid, rating, text, plat, "2025-01-16", "2025-01-28")

    # Sort by date
    rows.sort(key=lambda x: x[6])
    write_csv("reviews.csv", ["review_id", "user_id", "order_id", "rating", "text", "platform", "created_at"], rows)
    return rows


# ===================== 10. SUPPORT TICKETS =====================
def generate_support_tickets(users, orders):
    print("Generating support_tickets.csv...")
    rows = []
    tid = 1

    def add_ticket(uid, cat, subcat, desc, plat, priority, status, date_start, date_end, resolve_hours=None):
        nonlocal tid
        created = random_datetime(
            datetime.strptime(date_start, "%Y-%m-%d"),
            datetime.strptime(date_end, "%Y-%m-%d") + timedelta(hours=23)
        )
        if resolve_hours and status == "resolved":
            resolved = (created + timedelta(hours=resolve_hours)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            resolved = ""
        rows.append([
            f"TK{tid:04d}", uid, cat, subcat, desc, plat, priority, status,
            created.strftime("%Y-%m-%d %H:%M:%S"), resolved
        ])
        tid += 1

    # Dec 20 – Jan 9: ~6 normal tickets
    ios_users = [u[0] for u in users if u[5] == "ios"]
    android_users = [u[0] for u in users if u[5] == "android"]
    web_users = [u[0] for u in users if u[5] == "web"]

    add_ticket(random.choice(android_users), "delivery", "late_delivery", "My order was 30 minutes late. The tracker showed the driver going in the wrong direction.", "android", "medium", "resolved", "2024-12-20", "2024-12-23", 6)
    add_ticket(random.choice(web_users), "account", "login_issue", "Can't log into my account. Password reset email never arrives.", "web", "medium", "resolved", "2024-12-22", "2024-12-26", 4)
    add_ticket(random.choice(ios_users), "ui_bug", "display_issue", "Menu item images are overlapping with the text on smaller iPhone screens. Hard to read descriptions.", "ios", "low", "resolved", "2024-12-24", "2024-12-28", 12)
    add_ticket(random.choice(android_users), "delivery", "wrong_order", "Received completely wrong order. Got sushi instead of pizza.", "android", "high", "resolved", "2024-12-27", "2024-12-30", 3)
    add_ticket(random.choice(ios_users), "promo", "code_not_working", "Holiday promo code FESTIVE24 isn't applying the discount.", "ios", "low", "resolved", "2024-12-29", "2025-01-02", 8)
    add_ticket(random.choice(web_users), "account", "profile_update", "Can't update my delivery address. Save button doesn't respond.", "web", "medium", "resolved", "2025-01-05", "2025-01-08", 5)

    # Jan 10-15: ~8 payment tickets
    add_ticket(random.choice(ios_users), "payment", "failure", "Payment fails every time at the final step. Using iPhone 15 with Apple Pay. Error says 'Something went wrong'.", "ios", "high", "open", "2025-01-10", "2025-01-11")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment processing takes over 30 seconds and then times out. Tried 4 times.", "ios", "high", "open", "2025-01-10", "2025-01-12")
    add_ticket(random.choice(ios_users), "checkout", "payment_error", "Can't complete checkout. Apple Pay just spins and eventually shows an error.", "ios", "high", "in_progress", "2025-01-11", "2025-01-13")
    add_ticket(random.choice(ios_users), "payment", "failure", "Credit card payment not working on iOS app. Same card works fine on the website.", "ios", "high", "in_progress", "2025-01-12", "2025-01-14")
    add_ticket(random.choice(android_users), "payment", "failure", "Payment failed once but worked on retry. Just wanted to report it.", "android", "medium", "resolved", "2025-01-12", "2025-01-14", 6)
    add_ticket(random.choice(ios_users), "payment", "timeout", "Every payment attempt times out. iPhone SE, tried both Apple Pay and credit card.", "ios", "high", "open", "2025-01-13", "2025-01-15")
    add_ticket(random.choice(ios_users), "payment", "generic_error", "Getting 'Payment could not be processed' error on every order attempt.", "ios", "critical", "open", "2025-01-14", "2025-01-15")
    add_ticket(random.choice(ios_users), "checkout", "payment_error", "Checkout completely broken. The payment step hangs for a long time then fails.", "ios", "critical", "in_progress", "2025-01-14", "2025-01-15")

    # Jan 16-28: ~26 tickets
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment times out every time. Been trying for a week. iPhone 14 Pro.", "ios", "critical", "open", "2025-01-16", "2025-01-17")
    add_ticket(random.choice(ios_users), "payment", "failure", "Apple Pay completely non-functional. 'Gateway timeout' error.", "ios", "critical", "in_progress", "2025-01-16", "2025-01-18")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Can't order food. Payment always times out. This is ridiculous.", "ios", "critical", "open", "2025-01-17", "2025-01-18")
    add_ticket(random.choice(ios_users), "payment", "retry_unavailable", "Payment fails and there's no retry button. Have to start the whole order over.", "ios", "high", "open", "2025-01-17", "2025-01-19")
    add_ticket(random.choice(ios_users), "payment", "generic_error", "Generic 'Something went wrong' error on every payment attempt. No useful info.", "ios", "critical", "in_progress", "2025-01-18", "2025-01-19")
    add_ticket(random.choice(ios_users), "payment", "failure", "iOS payment broken for 10+ days. When will this be fixed?", "ios", "critical", "open", "2025-01-18", "2025-01-20")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment gateway timeout. Tried credit card, Apple Pay, all fail on iPhone.", "ios", "critical", "open", "2025-01-19", "2025-01-20")
    add_ticket(random.choice(ios_users), "payment", "failure", "My wife's Android phone works fine. My iPhone can't process any payment.", "ios", "high", "open", "2025-01-19", "2025-01-21")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment hangs for 30+ seconds then shows timeout error. Every single time.", "ios", "critical", "open", "2025-01-20", "2025-01-21")
    add_ticket(random.choice(ios_users), "payment", "generic_error", "Error: PAYMENT_PROVIDER_ERROR. What does this mean? Can't order anything.", "ios", "critical", "in_progress", "2025-01-20", "2025-01-22")
    add_ticket(random.choice(web_users), "promo", "code_not_working", "Promo code WINTER25 isn't working. It should give 15% off.", "web", "low", "resolved", "2025-01-20", "2025-01-23", 10)
    add_ticket(random.choice(ios_users), "payment", "failure", "Switched to competitor because FoodDash payments are broken on iOS.", "ios", "critical", "open", "2025-01-21", "2025-01-22")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment timeout again. This has been going on for almost 2 weeks!", "ios", "critical", "open", "2025-01-21", "2025-01-23")
    add_ticket(random.choice(ios_users), "payment", "retry_unavailable", "No retry option after payment fails. Have to re-add all items to cart.", "ios", "high", "open", "2025-01-22", "2025-01-23")
    add_ticket(random.choice(ios_users), "payment", "failure", "URGENT: Cannot process any payment on iPhone. Losing customers.", "ios", "critical", "open", "2025-01-22", "2025-01-24")
    add_ticket(random.choice(android_users), "delivery", "late_delivery", "Delivery was 45 minutes late. Driver seemed lost.", "android", "medium", "resolved", "2025-01-22", "2025-01-25", 4)
    add_ticket(random.choice(ios_users), "payment", "timeout", "Gateway timeout on every order. Updated app, restarted phone, nothing helps.", "ios", "critical", "open", "2025-01-23", "2025-01-24")
    add_ticket(random.choice(ios_users), "payment", "generic_error", "Getting different errors now - sometimes timeout, sometimes provider error.", "ios", "critical", "in_progress", "2025-01-23", "2025-01-25")
    add_ticket(random.choice(web_users), "account", "profile_update", "Can't update my delivery address. The save button doesn't do anything.", "web", "medium", "in_progress", "2025-01-24", "2025-01-26")
    add_ticket(random.choice(ios_users), "payment", "failure", "Haven't been able to order in 2 weeks. All iOS users I know have this issue.", "ios", "critical", "open", "2025-01-24", "2025-01-25")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment timeout. Tried 8 times today. Only succeeded once after waiting 45 seconds.", "ios", "critical", "open", "2025-01-25", "2025-01-26")
    add_ticket(random.choice(ios_users), "payment", "failure", "Credit card gets charged but order shows as failed. Had to dispute with bank.", "ios", "critical", "open", "2025-01-25", "2025-01-27")
    add_ticket(random.choice(ios_users), "payment", "retry_unavailable", "Why is there no retry button? Making me rebuild my cart from scratch every time.", "ios", "high", "open", "2025-01-26", "2025-01-27")
    add_ticket(random.choice(ios_users), "payment", "timeout", "Payment service is still broken on iPhone. It's been 17 days. Please fix this.", "ios", "critical", "open", "2025-01-27", "2025-01-28")
    add_ticket(random.choice(ios_users), "payment", "generic_error", "Constant payment errors on iOS. Considering deleting the app permanently.", "ios", "critical", "open", "2025-01-27", "2025-01-28")
    add_ticket(random.choice(ios_users), "payment", "failure", "iOS payment completely broken. Android works fine. Something is clearly wrong with the iOS payment path.", "ios", "critical", "open", "2025-01-28", "2025-01-28")

    rows.sort(key=lambda x: x[8])
    write_csv("support_tickets.csv",
              ["ticket_id", "user_id", "category", "subcategory", "description", "platform", "priority", "status", "created_at", "resolved_at"],
              rows)
    return rows


# ===================== 11. USABILITY STUDY =====================
def generate_usability_study():
    print("Generating usability_study.md...")
    content = """# FoodDash Payment Flow Usability Study

## Study Overview

**Type:** Moderated usability study
**Participants:** n=20
**Date:** January 18-22, 2025
**Facilitator:** UX Research Team (Rachel Kim, Lead Researcher)
**Objective:** Evaluate the end-to-end ordering and payment experience across platforms

Participants were recruited from active FoodDash users across iOS (n=10), Android (n=6), and Web (n=4) platforms. Each session lasted approximately 30 minutes and involved completing a series of ordering tasks.

---

## December Baseline (Previous Study)

A baseline usability study was conducted **December 5-8, 2024** with n=15 participants.

| Metric | December Baseline |
|--------|------------------|
| Payment flow satisfaction score | 4.2 / 5.0 |
| Task completion rate (place an order) | 92% |
| Average payment processing time | 3.2 seconds |
| Users reporting payment issues | 1/15 (6.7%) |
| Average time from checkout to confirmation | 8.4 seconds |

**Notable findings from December:**
- Payment flow was rated as "intuitive" by 13/15 participants
- One participant experienced a payment failure due to expired card (expected behavior)
- Restaurant search was the primary area of friction (addressed in Dec 18 update)
- Overall app satisfaction: 4.4/5.0

---

## January Findings

### Task Completion

| Metric | December Baseline | January Study | Change |
|--------|------------------|---------------|--------|
| Task completion rate | 92% | 54% | -38pp |
| Average payment processing time | 3.2s | 12.8s | +300% |
| Payment flow satisfaction | 4.2/5 | 1.8/5 | -57% |
| Users experiencing payment delays >5s | 1/15 | 8/20 | Significant increase |
| Users who abandoned checkout | 1/15 | 9/20 | Significant increase |

### Platform Comparison

| Platform | Task Completion Rate | Avg Processing Time | Payment Errors Observed |
|----------|---------------------|--------------------|-----------------------|
| iOS (n=10) | 41% | 18.3s | 7/10 participants |
| Android (n=6) | 89% | 4.1s | 1/6 participants |
| Web (n=4) | 86% | 3.8s | 0/4 participants |

**Note:** The disparity between iOS and other platforms was stark and consistent across all iOS test devices (iPhone 14, iPhone 15, iPhone SE).

---

## Key Themes

### 1. Payment Timeouts (Reported by 8/10 iOS users)
Participants on iOS consistently experienced long payment processing times. The spinner would appear after tapping "Pay Now" and persist for 10-45 seconds before either succeeding or displaying an error.

> "I tapped pay and then just... waited. It felt like the app was frozen." — Participant 7 (iOS)

### 2. Confusing Error Messages
When payments failed, the error message displayed was: **"Something went wrong. Please try again."**

- No specific information about *what* went wrong
- No indication of whether the payment was actually charged
- 6/8 affected users expressed frustration with the vague messaging

> "Something went wrong? That's all you're going to tell me? Did it charge my card or not?" — Participant 3 (iOS)

### 3. No Retry Mechanism
After a payment failure, users were returned to the cart screen with no option to retry the payment. They had to go through the entire checkout flow again.

- Average time to re-attempt: 45 seconds
- 3 participants gave up after 2 failed attempts
- 2 participants gave up after 3 failed attempts

> "Why do I have to re-enter everything? Just let me try again." — Participant 11 (iOS)

### 4. Inconsistent Behavior
Some participants noted that the same payment method would fail multiple times and then inexplicably succeed, suggesting an intermittent issue rather than a permanent one.

### 5. Cart Abandonment
9 out of 20 participants abandoned their cart during the study. All 9 were iOS users.

---

## Workarounds Observed

During the study, participants independently discovered or attempted several workarounds:

1. **Switched to Android device** — 3 iOS participants asked if they could try on a different device. When allowed, all 3 successfully completed payment on an Android phone.
2. **Used PayPal instead of Apple Pay** — 2 participants switched payment methods. One succeeded with PayPal (after 2 Apple Pay failures), one still failed.
3. **Asked friend to order** — 1 participant said they would ask their friend (who has an Android phone) to place the order for them.

---

## Risk Assessment

### Churn Indicators
- **4 out of 20 participants** mentioned they were considering switching to a competitor app (UberEats, DoorDash, Grubhub)
- **2 participants** stated they had already started using a competitor due to ongoing payment issues
- **3 participants** said they would "give it one more week" before switching

### Sentiment Analysis
- iOS user satisfaction: 1.4/5.0 (down from 4.3/5.0 in December)
- Android user satisfaction: 4.1/5.0 (stable)
- Web user satisfaction: 4.0/5.0 (stable)

---

## Recommendations

1. **Improve error messaging** — Replace "Something went wrong" with specific, actionable error messages. Indicate clearly whether the payment was charged.

2. **Add retry mechanism** — Allow users to retry payment from the checkout screen without re-entering the full flow. Preserve cart state.

3. **Investigate iOS-specific payment issue** — The data strongly suggests a platform-specific regression. The payment processing path on iOS should be investigated urgently. The issue appears to affect all payment methods on iOS, but Apple Pay is disproportionately impacted.

4. **Add payment status indicator** — Show real-time processing status during payment (e.g., "Connecting to payment provider...", "Processing payment...", "Confirming with bank...").

5. **Implement timeout handling** — If payment processing exceeds 10 seconds, show a status update. If it exceeds 30 seconds, offer to cancel and retry.

---

## Appendix: Study Participants

| ID | Platform | Device | Payment Method | Task Completed |
|----|----------|--------|---------------|----------------|
| P1 | iOS | iPhone 15 | Apple Pay | No |
| P2 | iOS | iPhone 14 | Credit Card | No |
| P3 | iOS | iPhone 15 Pro | Apple Pay | No |
| P4 | Android | Pixel 7 | Google Pay | Yes |
| P5 | iOS | iPhone SE | Credit Card | Yes (3rd attempt) |
| P6 | Web | Chrome | Credit Card | Yes |
| P7 | iOS | iPhone 14 | Apple Pay | No |
| P8 | Android | Samsung S23 | Credit Card | Yes |
| P9 | iOS | iPhone 15 | Apple Pay | No |
| P10 | Web | Safari | PayPal | Yes |
| P11 | iOS | iPhone 14 Pro | Credit Card | No |
| P12 | Android | Pixel 7 | Google Pay | Yes |
| P13 | iOS | iPhone 15 | Apple Pay | Yes (4th attempt) |
| P14 | Android | Samsung S23 | Credit Card | Yes |
| P15 | Web | Chrome | Credit Card | Yes |
| P16 | iOS | iPhone SE | Apple Pay | No |
| P17 | Android | Samsung A54 | Google Pay | Yes |
| P18 | iOS | iPhone 14 | Credit Card | Yes (2nd attempt) |
| P19 | Web | Firefox | PayPal | Yes |
| P20 | Android | Pixel 7 Pro | Google Pay | No |
"""
    write_md("usability_study.md", content)


# ===================== 12. UX CHANGELOG =====================
def generate_ux_changelog():
    print("Generating ux_changelog.csv...")
    rows = [
        ["2024-12-18", "feature", "Added restaurant category filters", "search", "all"],
        ["2024-12-22", "feature", "Holiday promo banner", "homepage", "all"],
        ["2024-12-28", "bugfix", "Fixed menu item image loading on slow connections", "restaurant_page", "all"],
        ["2025-01-03", "ab_test", "Testing new cart summary layout (50% of users)", "cart", "all"],
        ["2025-01-08", "feature", "Updated restaurant search ranking algorithm", "search", "all"],
        ["2025-01-10", "feature", "New payment confirmation animation", "checkout", "all"],
        ["2025-01-12", "bugfix", "Fixed checkout button alignment on small screens", "checkout", "ios"],
        ["2025-01-15", "feature", "Added order tracking real-time updates", "order_tracking", "all"],
        ["2025-01-18", "bugfix", "Fixed push notification permission prompt", "notifications", "ios"],
        ["2025-01-20", "ab_test", "Testing simplified checkout flow (30% of users)", "checkout", "all"],
        ["2025-01-25", "bugfix", "Fixed restaurant rating display rounding", "restaurant_page", "all"],
    ]
    write_csv("ux_changelog.csv", ["date", "change_type", "description", "affected_area", "platform"], rows)


# ===================== 13. DEPLOYMENTS =====================
def generate_deployments():
    print("Generating deployments.csv...")
    rows = [
        ["DEP001", "catalog_service", "Added restaurant category filters", "sarah.chen", "2024-12-18 10:30:00", "yes", gen_commit_hash()],
        ["DEP002", "notification_service", "Holiday promo notification batch job", "mike.johnson", "2024-12-22 14:15:00", "yes", gen_commit_hash()],
        ["DEP003", "catalog_service", "Image CDN optimization", "sarah.chen", "2024-12-28 09:45:00", "yes", gen_commit_hash()],
        ["DEP004", "user_service", "Updated user profile caching layer", "alex.kumar", "2025-01-03 11:00:00", "yes", gen_commit_hash()],
        ["DEP005", "search_service", "New restaurant ranking algorithm", "emily.wong", "2025-01-05 16:30:00", "yes", gen_commit_hash()],
        ["DEP006", "search_service", "Search index rebuild with new schema", "emily.wong", "2025-01-08 08:00:00", "yes", gen_commit_hash()],
        ["DEP007", "payment_service", "Migrated to PayStream v3 payment gateway", "david.park", "2025-01-10 06:00:00", "yes", gen_commit_hash()],
        ["DEP008", "checkout_service", "Checkout button CSS fix for iOS small screens", "lisa.taylor", "2025-01-12 13:20:00", "yes", gen_commit_hash()],
        ["DEP009", "payment_service", "Hotfix: increased PayStream timeout from 5s to 10s", "david.park", "2025-01-14 09:30:00", "yes", gen_commit_hash()],
        ["DEP010", "search_service", "Deployed new ranking model v2", "emily.wong", "2025-01-17 15:00:00", "yes", gen_commit_hash()],
        ["DEP011", "payment_service", "Added retry logic for PayStream timeout errors", "david.park", "2025-01-20 10:45:00", "yes", gen_commit_hash()],
        ["DEP012", "notification_service", "Fixed email template rendering bug", "mike.johnson", "2025-01-22 11:30:00", "yes", gen_commit_hash()],
        ["DEP013", "catalog_service", "Menu image CDN migration to CloudFront", "sarah.chen", "2025-01-25 14:00:00", "yes", gen_commit_hash()],
        ["DEP014", "user_service", "Added user deletion workflow for GDPR", "alex.kumar", "2025-01-28 09:00:00", "yes", gen_commit_hash()],
    ]
    write_csv("deployments.csv",
              ["deploy_id", "service", "description", "author", "timestamp", "rollback_available", "commit_hash"],
              rows)


# ===================== 14. SERVICE METRICS =====================
def generate_service_metrics():
    print("Generating service_metrics.csv...")
    services = {
        "payment_service": {"p50": 120, "p95": 280, "p99": 450, "error_rate": 0.3, "requests": 15000},
        "checkout_service": {"p50": 80, "p95": 180, "p99": 300, "error_rate": 0.1, "requests": 20000},
        "catalog_service": {"p50": 45, "p95": 120, "p99": 200, "error_rate": 0.05, "requests": 50000},
        "user_service": {"p50": 30, "p95": 80, "p99": 150, "error_rate": 0.08, "requests": 30000},
        "notification_service": {"p50": 50, "p95": 150, "p99": 250, "error_rate": 0.1, "requests": 10000},
        "search_service": {"p50": 60, "p95": 160, "p99": 280, "error_rate": 0.05, "requests": 40000},
    }

    rows = []
    current = START_DATE
    while current.date() <= END_DATE.date():
        date_str = current.strftime("%Y-%m-%d")
        date = current.date()
        is_post = current >= MIGRATION_DATE
        days_after = (current - MIGRATION_DATE).days if is_post else 0

        for svc, baseline in services.items():
            p50 = baseline["p50"]
            p95 = baseline["p95"]
            p99 = baseline["p99"]
            err = baseline["error_rate"]
            reqs = baseline["requests"]

            if svc == "payment_service" and is_post:
                if days_after <= 2:
                    p50 = 180; p95 = 450; p99 = 1200; err = 2.1; reqs = 14000
                elif days_after <= 5:
                    p50 = 280; p95 = 800; p99 = 2500; err = 3.8; reqs = 13000
                    # Brief dip from hotfix on Jan 14 (days_after=4)
                    if days_after == 4:
                        err = 2.5; p50 = 220; p95 = 600; p99 = 1800
                elif days_after <= 10:
                    p50 = 400; p95 = 1200; p99 = 3500; err = 4.5; reqs = 12000
                else:
                    progress = min(1.0, (days_after - 10) / 11.0)
                    p50 = int(500 + progress * 100)
                    p95 = 1500
                    p99 = int(4000 + progress * 500)
                    err = 5.0 + progress * 0.8
                    reqs = int(11500 - progress * 500)

            # Red herring: search_service p99 spike on Jan 8
            if svc == "search_service" and date == datetime(2025, 1, 8).date():
                p99 = 800

            # Red herring: notification_service error spike Jan 20-22
            if svc == "notification_service" and datetime(2025, 1, 20).date() <= date <= datetime(2025, 1, 22).date():
                err = 0.8

            # Apply jitter
            p50_j = max(1, int(jitter(p50, 0.08)))
            p95_j = max(p50_j + 1, int(jitter(p95, 0.08)))
            p99_j = max(p95_j + 1, int(jitter(p99, 0.08)))
            err_j = max(0.0, round(jitter(err, 0.10), 2))
            reqs_j = max(1000, int(jitter(reqs, 0.07)))
            err_count = max(0, int(reqs_j * err_j / 100))

            rows.append([date_str, svc, p50_j, p95_j, p99_j, err_j, err_count, reqs_j])

        current += timedelta(days=1)

    write_csv("service_metrics.csv",
              ["date", "service", "p50_ms", "p95_ms", "p99_ms", "error_rate_pct", "error_count", "request_count"],
              rows)


# ===================== 15. SYSTEM ARCHITECTURE =====================
def generate_system_architecture():
    print("Generating system_architecture.md...")
    content = """# FoodDash System Architecture

## Overview

FoodDash is a food delivery platform built on a microservice architecture running on AWS. The system consists of 6 core microservices, a PostgreSQL database cluster, Redis caching layer, and integrations with external payment and notification providers.

**Infrastructure:** AWS (ECS for container orchestration, RDS for PostgreSQL, ElastiCache for Redis, CloudFront CDN for static assets and images)

---

## Services

### 1. Catalog Service
- **Purpose:** Manages restaurant listings, menus, categories, and item availability
- **Stack:** Python (FastAPI), PostgreSQL
- **Port:** 8001
- **Dependencies:** PostgreSQL (RDS), Redis (ElastiCache), CloudFront CDN (images)
- **Owner:** Sarah Chen

### 2. Search Service
- **Purpose:** Restaurant and menu item search, ranking, and recommendations
- **Stack:** Python (FastAPI), Elasticsearch
- **Port:** 8002
- **Dependencies:** Elasticsearch cluster, Catalog Service (for index updates)
- **Owner:** Emily Wong

### 3. User Service
- **Purpose:** User authentication, profiles, preferences, and session management
- **Stack:** Node.js (Express), PostgreSQL
- **Port:** 8003
- **Dependencies:** PostgreSQL (RDS), Redis (session cache)
- **Owner:** Alex Kumar

### 4. Checkout Service
- **Purpose:** Shopping cart management, order creation, checkout flow orchestration
- **Stack:** Python (FastAPI), PostgreSQL
- **Port:** 8004
- **Dependencies:** Payment Service, Catalog Service, User Service, PostgreSQL (RDS)
- **Owner:** Lisa Taylor

### 5. Payment Service
- **Purpose:** Payment processing, refunds, transaction management
- **Stack:** Java (Spring Boot), PostgreSQL
- **Port:** 8005
- **Dependencies:** External PayStream API (payment gateway), PostgreSQL (RDS)
- **Owner:** David Park
- **Note:** Recently migrated from PayStream v2 to PayStream v3 API (January 10, 2025)

### 6. Notification Service
- **Purpose:** Push notifications, email, and SMS delivery
- **Stack:** Node.js (Express), Redis (queue)
- **Port:** 8006
- **Dependencies:** AWS SES (email), Firebase Cloud Messaging (push), Twilio (SMS)
- **Owner:** Mike Johnson

---

## Service Dependency Diagram

```
                    ┌─────────────┐
                    │   Client    │
                    │ (iOS/Android│
                    │    /Web)    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  API Gateway │
                    │  (AWS ALB)   │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────────┐
          │                │                    │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────────▼────────┐
    │  Catalog   │   │  Search   │   │   User Service   │
    │  Service   │   │  Service  │   │                  │
    └─────┬─────┘   └─────┬─────┘   └─────────┬────────┘
          │               │                    │
          │         ┌─────┘                    │
          │         │                          │
    ┌─────▼─────────▼──────────────────────────▼───┐
    │              Checkout Service                  │
    │      (cart management, order creation)         │
    └─────────────────────┬────────────────────────┘
                          │
                    ┌─────▼──────┐
                    │  Payment   │
                    │  Service   │
                    └─────┬──────┘
                          │
                    ┌─────▼──────────┐
                    │  PayStream API  │
                    │  (External)     │
                    │  v2 → v3        │
                    └─────┬──────────┘
                          │
                    ┌─────▼──────┐
                    │    Bank /   │
                    │  Card Issuer│
                    └────────────┘

    ┌──────────────────┐
    │  Notification     │  (triggered by Checkout Service
    │  Service          │   after order events)
    └──────────────────┘
```

---

## Payment Flow (Detailed)

The payment flow is the critical path for order completion:

```
1. User taps "Pay Now" in the app
      │
2. Client → Checkout Service: POST /api/v1/orders/{id}/pay
      │
3. Checkout Service → Payment Service: POST /api/v1/payments/process
      │
4. Payment Service → PayStream Gateway: POST /v3/transactions
   (Previously: POST /v2/transactions — migrated Jan 10, 2025)
      │
5. PayStream → Bank/Card Issuer: Authorization request
      │
6. Bank → PayStream → Payment Service → Checkout Service → Client
   (Response propagates back through the chain)
```

**Timeout Configuration:**
- Client → Checkout Service: 30s timeout
- Checkout Service → Payment Service: 15s timeout
- Payment Service → PayStream: 10s timeout (was 5s, increased Jan 14 hotfix)

**Payment Methods Supported:**
- Credit Card (all platforms)
- Apple Pay (iOS only — routes through iOS PayStream SDK)
- Google Pay (Android only — routes through Android PayStream SDK)
- PayPal (all platforms — routes through PayPal API, not PayStream)

---

## Database

- **PostgreSQL 15** on AWS RDS (Multi-AZ deployment)
- **Primary instance:** db.r6g.xlarge
- **Read replicas:** 2 (us-east-1b, us-east-1c)
- **Key tables:** users, restaurants, menu_items, orders, order_items, payments, sessions

---

## Caching

- **Redis 7** on AWS ElastiCache
- **Cluster mode:** Enabled (3 shards)
- **Use cases:**
  - User session data (TTL: 24h)
  - Restaurant menu cache (TTL: 15min)
  - Search results cache (TTL: 5min)
  - Rate limiting

---

## CDN

- **AWS CloudFront** for static asset delivery
- Restaurant images, menu item photos
- Recently migrated image storage to CloudFront (Jan 25, 2025)

---

## Monitoring & Observability

- **Metrics:** Datadog (service latency, error rates, throughput)
- **Logging:** AWS CloudWatch Logs → Elasticsearch
- **Tracing:** Datadog APM (distributed tracing across services)
- **Alerting:** PagerDuty integration for critical alerts

---

## Recent Changes

| Date | Service | Change |
|------|---------|--------|
| Dec 18 | Catalog | Added restaurant category filters |
| Dec 28 | Catalog | Image CDN optimization |
| Jan 5 | Search | New ranking algorithm |
| Jan 8 | Search | Index rebuild with new schema |
| **Jan 10** | **Payment** | **Migrated to PayStream v3 payment gateway** |
| Jan 14 | Payment | Hotfix: increased PayStream timeout 5s → 10s |
| Jan 20 | Payment | Added retry logic for timeout errors |
| Jan 25 | Catalog | CloudFront CDN migration |
"""
    write_md("system_architecture.md", content)


# ===================== 16. PAYMENT ERRORS SUMMARY =====================
def generate_payment_errors_summary(payments):
    print("Generating payment_errors_summary.csv...")
    # Aggregate errors by date, error_code, platform
    from collections import defaultdict
    agg = defaultdict(int)

    for p in payments:
        date_str = p[9][:10]  # created_at date portion
        error_code = p[8] if p[8] else "null"
        platform = "ios"  # need to figure out platform from order
        # We stored method which tells us platform indirectly, but let's use the order lookup
        # Actually payments don't have platform directly. Let's derive from method.
        method = p[3]
        if method == "apple_pay":
            platform = "ios"
        elif method == "google_pay":
            platform = "android"
        else:
            # Need to look at order data - but we don't have easy lookup here
            # We'll use a simpler approach: just track from the payment provider + method
            # Actually let's just re-derive. We need order platform.
            # The payments list doesn't have platform. Let's rebuild.
            pass

    # Better approach: build from orders which have platform
    # Re-aggregate from payments with order lookup
    order_platform = {}
    # We need orders... let's pass them in. Actually, let's just regenerate from payments data.
    # payments: [payment_id, order_id, user_id, method, provider, status, amount, processing_time_ms, error_code, created_at]
    # We don't have platform in payments. Let's add it via the method heuristic + random assignment for credit_card/paypal

    # Actually, we should aggregate from payments joined with orders. Since we can't easily do that here,
    # let's generate this summary directly from the scenario parameters.

    rows = []
    error_codes = ["GATEWAY_TIMEOUT", "PAYMENT_PROVIDER_ERROR", "INSUFFICIENT_FUNDS", "CARD_DECLINED", "NETWORK_ERROR"]
    platforms = ["ios", "android", "web"]

    current = START_DATE
    while current.date() <= END_DATE.date():
        date_str = current.strftime("%Y-%m-%d")
        is_post = current >= MIGRATION_DATE
        days_after = (current - MIGRATION_DATE).days if is_post else 0

        if not is_post:
            # Pre migration: low error counts
            # ~5-10 errors/day total, mostly INSUFFICIENT_FUNDS and CARD_DECLINED
            for plat in platforms:
                plat_weight = {"ios": 0.45, "android": 0.35, "web": 0.20}[plat]
                for ec in ["INSUFFICIENT_FUNDS", "CARD_DECLINED"]:
                    count = max(0, int(jitter(3 * plat_weight, 0.4)))
                    if count > 0:
                        rows.append([date_str, ec, count, plat])
                # Rare timeout
                if random.random() < 0.15:
                    rows.append([date_str, "GATEWAY_TIMEOUT", 1, plat])
        else:
            degradation = min(1.0, days_after / 21.0)

            # iOS errors spike
            ios_timeout = max(0, int(jitter(15 + degradation * 45, 0.15)))
            ios_provider = max(0, int(jitter(10 + degradation * 25, 0.15)))
            ios_network = max(0, int(jitter(2 + degradation * 5, 0.2)))
            ios_insuf = max(0, int(jitter(2, 0.3)))
            ios_declined = max(0, int(jitter(1, 0.4)))

            if ios_timeout > 0: rows.append([date_str, "GATEWAY_TIMEOUT", ios_timeout, "ios"])
            if ios_provider > 0: rows.append([date_str, "PAYMENT_PROVIDER_ERROR", ios_provider, "ios"])
            if ios_network > 0: rows.append([date_str, "NETWORK_ERROR", ios_network, "ios"])
            if ios_insuf > 0: rows.append([date_str, "INSUFFICIENT_FUNDS", ios_insuf, "ios"])
            if ios_declined > 0: rows.append([date_str, "CARD_DECLINED", ios_declined, "ios"])

            # Android: mild
            and_timeout = max(0, int(jitter(3 + degradation * 5, 0.2)))
            and_provider = max(0, int(jitter(2 + degradation * 3, 0.2)))
            and_insuf = max(0, int(jitter(2, 0.3)))
            and_declined = max(0, int(jitter(1, 0.4)))

            if and_timeout > 0: rows.append([date_str, "GATEWAY_TIMEOUT", and_timeout, "android"])
            if and_provider > 0: rows.append([date_str, "PAYMENT_PROVIDER_ERROR", and_provider, "android"])
            if and_insuf > 0: rows.append([date_str, "INSUFFICIENT_FUNDS", and_insuf, "android"])
            if and_declined > 0: rows.append([date_str, "CARD_DECLINED", and_declined, "android"])

            # Web: mild
            web_timeout = max(0, int(jitter(1 + degradation * 3, 0.25)))
            web_provider = max(0, int(jitter(1 + degradation * 2, 0.25)))
            web_insuf = max(0, int(jitter(1, 0.4)))

            if web_timeout > 0: rows.append([date_str, "GATEWAY_TIMEOUT", web_timeout, "web"])
            if web_provider > 0: rows.append([date_str, "PAYMENT_PROVIDER_ERROR", web_provider, "web"])
            if web_insuf > 0: rows.append([date_str, "INSUFFICIENT_FUNDS", web_insuf, "web"])

        current += timedelta(days=1)

    write_csv("payment_errors_summary.csv", ["date", "error_code", "count", "platform"], rows)


# ===================== MAIN =====================
def main():
    print("=" * 60)
    print("FoodDash Scenario Data Generator")
    print("Checkout Conversion Drop - PayStream v3 Migration")
    print("=" * 60)
    print(f"Output directory: {TABLES_DIR}")
    print()

    # 1. Users
    users = generate_users(5000)

    # 2. Restaurants
    restaurants = generate_restaurants(users)

    # 3. Menu items
    menu_items, restaurant_menu_map = generate_menu_items(restaurants)

    # 4. Orders
    orders = generate_orders(users, restaurants, restaurant_menu_map)

    # 5. Order items
    order_items = generate_order_items(orders, restaurant_menu_map)

    # 6. Drivers
    drivers = generate_drivers(200)

    # 7. Payments
    payments = generate_payments(orders)

    # 8. Session events
    session_events = generate_session_events(users, orders)

    # 9. Reviews
    reviews = generate_reviews(users, orders)

    # 10. Support tickets
    support_tickets = generate_support_tickets(users, orders)

    # 11. Usability study
    generate_usability_study()

    # 12. UX Changelog
    generate_ux_changelog()

    # 13. Deployments
    generate_deployments()

    # 14. Service metrics
    generate_service_metrics()

    # 15. System architecture
    generate_system_architecture()

    # 16. Payment errors summary
    generate_payment_errors_summary(payments)

    print()
    print("=" * 60)
    print("Data generation complete!")
    print(f"All files written to: {TABLES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
