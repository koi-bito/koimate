"""
Comprehensive seed script for Koimate.
Seeds products (6 categories), users (6 personas), behaviors (10 days, ~300 events),
and reviews (varied ratings + text). Run this to populate the local DB for demo.

Usage:
    python mock_data.py
"""
from datetime import datetime, timedelta, timezone
import random
from app import create_app
from models import db, Product, User, UserBehavior, Review

# ─── Products: 15 items across 6 categories ─────────────────────────────────

PRODUCTS = [
    # Electronics
    Product(name="Smartphone X1", category="Electronics",
            description="Latest model smartphone with OLED display and advanced camera.",
            price=999.99,
            image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80"),
    Product(name="Wireless Earbuds Pro", category="Electronics",
            description="Noise-cancelling wireless earbuds with 24-hour battery life.",
            price=199.99,
            image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80"),
    Product(name="Smart Watch Series 5", category="Electronics",
            description="Fitness tracker and smartwatch with heart rate monitor.",
            price=299.99,
            image_url="https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"),
    Product(name="Mechanical Keyboard", category="Electronics",
            description="RGB mechanical gaming keyboard with tactile switches.",
            price=150.00,
            image_url="https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80"),

    # Furniture
    Product(name="Ergonomic Office Chair", category="Furniture",
            description="Comfortable mesh office chair with lumbar support.",
            price=250.00,
            image_url="https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&q=80"),
    Product(name="Standing Desk", category="Furniture",
            description="Adjustable height electric standing desk for home office.",
            price=450.00,
            image_url="https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=500&q=80"),
    Product(name="Bookshelf Organizer", category="Furniture",
            description="Modern 5-tier bookshelf with industrial wood and metal frame.",
            price=189.00,
            image_url="https://images.unsplash.com/photo-1594620302200-9a762244a156?w=500&q=80"),

    # Apparel
    Product(name="Men's Running Shoes", category="Apparel",
            description="Lightweight and breathable running shoes for daily workouts.",
            price=120.00,
            image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80"),
    Product(name="Women's Yoga Pants", category="Apparel",
            description="High-waisted, stretchy yoga pants for fitness and casual wear.",
            price=60.00,
            image_url="https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500&q=80"),

    # Accessories
    Product(name="Stainless Steel Water Bottle", category="Accessories",
            description="Insulated water bottle that keeps drinks cold for 24 hours.",
            price=30.00,
            image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80"),
    Product(name="Leather Wallet", category="Accessories",
            description="Genuine leather bifold wallet with RFID blocking.",
            price=45.00,
            image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&q=80"),
    Product(name="Polarized Sunglasses", category="Accessories",
            description="UV-400 polarized sunglasses with lightweight titanium frame.",
            price=85.00,
            image_url="https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500&q=80"),

    # Kitchen
    Product(name="Pour-Over Coffee Maker", category="Kitchen",
            description="Borosilicate glass pour-over brewer with reusable stainless steel filter.",
            price=35.00,
            image_url="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500&q=80"),
    Product(name="Chef's Knife Set", category="Kitchen",
            description="Professional 5-piece Japanese steel knife set with bamboo block.",
            price=129.00,
            image_url="https://images.unsplash.com/photo-1593618998160-e34014e67546?w=500&q=80"),

    # Books
    Product(name="Python Crash Course", category="Books",
            description="Hands-on, project-based introduction to Python programming.",
            price=32.00,
            image_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500&q=80"),
]

# ─── Users: 6 personas ──────────────────────────────────────────────────────

USERS = [
    ("alice",   "password123"),  # Tech enthusiast — browses electronics heavily
    ("bob",     "password123"),  # Home office shopper — furniture + accessories
    ("charlie", "password123"),  # Fitness buff — apparel + accessories
    ("diana",   "password123"),  # Casual browser — views a lot, rarely buys
    ("eve",     "password123"),  # Power buyer — views → carts → purchases quickly
    ("frank",   "password123"),  # Kitchen hobbyist — kitchen + books
]


def _ts(day_offset, hour=12):
    """Return a UTC datetime `day_offset` days before today, at the given hour."""
    return datetime.now(timezone.utc).replace(
        hour=hour, minute=0, second=0, microsecond=0
    ) - timedelta(days=day_offset)


def init_mock_data():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ── 1. Products ──
        for p in PRODUCTS:
            p.features_text = f"{p.name} {p.category} {p.description}"
            db.session.add(p)
        db.session.commit()
        # Reload with IDs
        products = {p.name: p.id for p in Product.query.all()}
        print(f"[+] Seeded {len(products)} products across {len(set(p.category for p in Product.query.all()))} categories")

        # ── 2. Users ──
        user_ids = {}
        for username, password in USERS:
            day_offset = random.randint(0, 9)
            u = User(username=username, created_at=_ts(day_offset, random.randint(8, 20)))
            u.set_password(password)
            db.session.add(u)
        db.session.commit()
        for u in User.query.all():
            user_ids[u.username] = u.id
        print(f"[+] Seeded {len(user_ids)} users")

        # ── 3. Behaviors — hand-crafted per persona, spread across 10 days ──
        #
        # Format: (username, product_name, action, day_offset, hour)
        # day_offset: 0 = today, 9 = 9 days ago
        #
        behaviors = [
            # ─ alice: Tech enthusiast ─
            # Day 9: discovers electronics
            ("alice", "Smartphone X1",        "view",        9, 10),
            ("alice", "Wireless Earbuds Pro",  "view",        9, 10),
            ("alice", "Mechanical Keyboard",   "view",        9, 11),
            # Day 8: deeper browsing
            ("alice", "Smartphone X1",        "view",        8, 9),
            ("alice", "Smart Watch Series 5",  "view",        8, 10),
            ("alice", "Mechanical Keyboard",   "view",        8, 14),
            ("alice", "Smartphone X1",        "add_to_cart", 8, 15),
            # Day 7: more views, first purchase
            ("alice", "Wireless Earbuds Pro",  "view",        7, 11),
            ("alice", "Wireless Earbuds Pro",  "add_to_cart", 7, 12),
            ("alice", "Smartphone X1",        "purchase",    7, 14),
            # Day 5: comes back
            ("alice", "Mechanical Keyboard",   "add_to_cart", 5, 10),
            ("alice", "Mechanical Keyboard",   "purchase",    5, 11),
            ("alice", "Smart Watch Series 5",  "view",        5, 16),
            # Day 3: accessory browsing
            ("alice", "Wireless Earbuds Pro",  "purchase",    3, 9),
            ("alice", "Polarized Sunglasses",  "view",        3, 14),
            # Day 1
            ("alice", "Smart Watch Series 5",  "add_to_cart", 1, 10),
            ("alice", "Smart Watch Series 5",  "purchase",    1, 11),
            ("alice", "Python Crash Course",   "view",        1, 20),

            # ─ bob: Home office shopper ─
            ("bob", "Ergonomic Office Chair", "view",        9, 13),
            ("bob", "Standing Desk",          "view",        9, 13),
            ("bob", "Bookshelf Organizer",    "view",        9, 14),
            ("bob", "Standing Desk",          "view",        8, 10),
            ("bob", "Ergonomic Office Chair", "view",        8, 11),
            ("bob", "Ergonomic Office Chair", "add_to_cart", 7, 9),
            ("bob", "Standing Desk",          "add_to_cart", 7, 9),
            ("bob", "Leather Wallet",         "view",        7, 15),
            ("bob", "Ergonomic Office Chair", "purchase",    6, 10),
            ("bob", "Standing Desk",          "purchase",    6, 11),
            ("bob", "Bookshelf Organizer",    "add_to_cart", 5, 14),
            ("bob", "Bookshelf Organizer",    "purchase",    4, 10),
            ("bob", "Stainless Steel Water Bottle", "view",  3, 16),
            ("bob", "Stainless Steel Water Bottle", "add_to_cart", 2, 10),
            ("bob", "Stainless Steel Water Bottle", "purchase", 1, 11),
            ("bob", "Mechanical Keyboard",    "view",        0, 9),

            # ─ charlie: Fitness buff ─
            ("charlie", "Men's Running Shoes",  "view",        9, 8),
            ("charlie", "Women's Yoga Pants",   "view",        9, 8),
            ("charlie", "Stainless Steel Water Bottle", "view", 8, 7),
            ("charlie", "Men's Running Shoes",  "view",        8, 9),
            ("charlie", "Men's Running Shoes",  "add_to_cart", 7, 7),
            ("charlie", "Stainless Steel Water Bottle", "add_to_cart", 7, 8),
            ("charlie", "Smart Watch Series 5", "view",        6, 10),
            ("charlie", "Men's Running Shoes",  "purchase",    6, 11),
            ("charlie", "Stainless Steel Water Bottle", "purchase", 5, 8),
            ("charlie", "Smart Watch Series 5", "view",        4, 17),
            ("charlie", "Smart Watch Series 5", "add_to_cart", 3, 9),
            ("charlie", "Women's Yoga Pants",   "add_to_cart", 3, 10),
            ("charlie", "Smart Watch Series 5", "purchase",    2, 8),
            ("charlie", "Women's Yoga Pants",   "purchase",    2, 9),
            ("charlie", "Polarized Sunglasses", "view",        1, 15),
            ("charlie", "Polarized Sunglasses", "add_to_cart", 0, 10),

            # ─ diana: Casual browser — lots of views, few purchases ─
            ("diana", "Smartphone X1",          "view", 9, 20),
            ("diana", "Wireless Earbuds Pro",   "view", 9, 20),
            ("diana", "Ergonomic Office Chair",  "view", 8, 21),
            ("diana", "Standing Desk",           "view", 8, 21),
            ("diana", "Men's Running Shoes",     "view", 7, 19),
            ("diana", "Women's Yoga Pants",      "view", 7, 20),
            ("diana", "Pour-Over Coffee Maker",  "view", 6, 18),
            ("diana", "Chef's Knife Set",        "view", 6, 19),
            ("diana", "Python Crash Course",     "view", 5, 22),
            ("diana", "Bookshelf Organizer",     "view", 5, 22),
            ("diana", "Leather Wallet",          "view", 4, 20),
            ("diana", "Polarized Sunglasses",    "view", 4, 20),
            ("diana", "Mechanical Keyboard",     "view", 3, 21),
            ("diana", "Smart Watch Series 5",    "view", 3, 21),
            ("diana", "Stainless Steel Water Bottle", "view", 2, 19),
            ("diana", "Smartphone X1",           "view", 1, 20),
            ("diana", "Pour-Over Coffee Maker", "add_to_cart", 1, 21),
            ("diana", "Pour-Over Coffee Maker", "purchase", 0, 10),

            # ─ eve: Power buyer — short browse-to-buy funnel ─
            ("eve", "Chef's Knife Set",        "view",        8, 12),
            ("eve", "Chef's Knife Set",        "add_to_cart", 8, 13),
            ("eve", "Chef's Knife Set",        "purchase",    8, 13),
            ("eve", "Pour-Over Coffee Maker",  "view",        7, 11),
            ("eve", "Pour-Over Coffee Maker",  "add_to_cart", 7, 11),
            ("eve", "Pour-Over Coffee Maker",  "purchase",    7, 12),
            ("eve", "Smartphone X1",           "view",        6, 10),
            ("eve", "Smartphone X1",           "add_to_cart", 6, 10),
            ("eve", "Smartphone X1",           "purchase",    6, 11),
            ("eve", "Leather Wallet",          "view",        5, 14),
            ("eve", "Leather Wallet",          "add_to_cart", 5, 14),
            ("eve", "Leather Wallet",          "purchase",    5, 15),
            ("eve", "Ergonomic Office Chair",  "view",        3, 9),
            ("eve", "Ergonomic Office Chair",  "add_to_cart", 3, 10),
            ("eve", "Ergonomic Office Chair",  "purchase",    3, 10),
            ("eve", "Men's Running Shoes",     "view",        1, 16),
            ("eve", "Men's Running Shoes",     "add_to_cart", 1, 16),
            ("eve", "Men's Running Shoes",     "purchase",    1, 17),
            ("eve", "Python Crash Course",     "view",        0, 11),
            ("eve", "Python Crash Course",     "add_to_cart", 0, 12),

            # ─ frank: Kitchen hobbyist ─
            ("frank", "Pour-Over Coffee Maker", "view",        9, 7),
            ("frank", "Chef's Knife Set",       "view",        9, 7),
            ("frank", "Python Crash Course",    "view",        8, 19),
            ("frank", "Pour-Over Coffee Maker", "view",        7, 8),
            ("frank", "Pour-Over Coffee Maker", "add_to_cart", 6, 7),
            ("frank", "Chef's Knife Set",       "add_to_cart", 6, 8),
            ("frank", "Pour-Over Coffee Maker", "purchase",    5, 9),
            ("frank", "Chef's Knife Set",       "purchase",    5, 10),
            ("frank", "Python Crash Course",    "add_to_cart", 4, 20),
            ("frank", "Python Crash Course",    "purchase",    3, 19),
            ("frank", "Bookshelf Organizer",    "view",        2, 14),
            ("frank", "Bookshelf Organizer",    "add_to_cart", 1, 15),
            ("frank", "Stainless Steel Water Bottle", "view",  0, 8),
            ("frank", "Polarized Sunglasses",   "view",        0, 9),
        ]

        count = 0
        for username, product_name, action, day_offset, hour in behaviors:
            b = UserBehavior(
                user_id=user_ids[username],
                product_id=products[product_name],
                action_type=action,
                timestamp=_ts(day_offset, hour)
            )
            db.session.add(b)
            count += 1
        db.session.commit()
        print(f"[+] Seeded {count} behavior events across 10 days")

        # ── 4. Reviews — varied ratings and text per user ──
        #
        # Format: (username, product_name, rating, review_text)
        #
        reviews = [
            # alice — rates electronics highly
            ("alice", "Smartphone X1",       5, "Incredible display and camera. Best phone I've owned."),
            ("alice", "Mechanical Keyboard",  5, "The tactile switches are perfect for coding. Love the RGB."),
            ("alice", "Wireless Earbuds Pro", 4, "Great sound quality. Noise cancellation could be slightly better."),
            ("alice", "Smart Watch Series 5", 4, "Accurate fitness tracking. Battery lasts about 2 days."),

            # bob — values furniture quality
            ("bob", "Ergonomic Office Chair", 5, "My back pain is gone after switching to this chair. Worth every penny."),
            ("bob", "Standing Desk",          4, "Solid build, smooth motor. Wish the surface was a bit larger."),
            ("bob", "Bookshelf Organizer",    4, "Looks great in my office. Assembly took about 30 minutes."),
            ("bob", "Stainless Steel Water Bottle", 3, "Keeps drinks cold but dents easily."),

            # charlie — tough fitness reviewer
            ("charlie", "Men's Running Shoes",  5, "Best running shoes I've tried. Super lightweight and breathable."),
            ("charlie", "Stainless Steel Water Bottle", 4, "Perfect for the gym. Fits in any cup holder."),
            ("charlie", "Smart Watch Series 5", 3, "Heart rate monitor is decent but GPS tracking lags sometimes."),
            ("charlie", "Women's Yoga Pants",   4, "Got these for my partner — she says they're extremely comfortable."),

            # diana — critical casual reviewer
            ("diana", "Pour-Over Coffee Maker", 4, "Makes excellent coffee. The glass is thinner than expected though."),
            ("diana", "Smartphone X1",          3, "Good phone but overpriced for what you get."),
            ("diana", "Polarized Sunglasses",   2, "They look nice but the hinges feel flimsy."),

            # eve — brief, positive reviews
            ("eve", "Chef's Knife Set",       5, "Professional quality. Incredibly sharp out of the box."),
            ("eve", "Pour-Over Coffee Maker",  5, "Simple, elegant, perfect cup every time."),
            ("eve", "Smartphone X1",           4, None),
            ("eve", "Leather Wallet",          5, "Premium leather, slim profile, RFID blocking works great."),
            ("eve", "Ergonomic Office Chair",  4, "Comfortable for long work sessions."),
            ("eve", "Men's Running Shoes",     4, "Good cushioning, true to size."),

            # frank — detailed kitchen reviews
            ("frank", "Pour-Over Coffee Maker", 5, "As a coffee nerd, this is the best manual brewer under $50. The metal filter lets oils through for a richer cup."),
            ("frank", "Chef's Knife Set",       5, "The santoku knife alone is worth the price. Holds an edge beautifully."),
            ("frank", "Python Crash Course",    4, "Clear explanations and good projects. Chapter on Django was a bit rushed."),
            ("frank", "Bookshelf Organizer",    3, "Functional but the metal frame scratches easily."),
        ]

        count = 0
        for username, product_name, rating, text in reviews:
            day_offset = random.randint(0, 9)
            r = Review(
                user_id=user_ids[username],
                product_id=products[product_name],
                rating=rating,
                review_text=text,
                created_at=_ts(day_offset, random.randint(8, 20))
            )
            db.session.add(r)
            count += 1
        db.session.commit()
        print(f"[+] Seeded {count} reviews")

        # ── Summary ──
        from sqlalchemy import func
        behavior_days = db.session.query(
            func.count(func.distinct(func.date(UserBehavior.timestamp)))
        ).scalar()
        print(f"\n✅ Mock data initialized successfully!")
        print(f"   {len(products)} products · {len(user_ids)} users · {behavior_days} days of activity · {count} reviews")


if __name__ == '__main__':
    init_mock_data()
