"""
Comprehensive seed script: products, users, behaviors, and reviews.
Run once to populate the local SQLite DB for testing.
"""
import random
from datetime import datetime, timedelta
from app import create_app
from models import db, Product, User, UserBehavior, Review


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ── Products ──
        products = [
            Product(name="Smartphone X1", category="Electronics", description="Latest model smartphone with OLED display and advanced camera.",  # noqa: E501
                    price=999.99, image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80"),
            Product(name="Wireless Earbuds Pro", category="Electronics", description="Noise-cancelling wireless earbuds with 24-hour battery life.",  # noqa: E501
                    price=199.99, image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80"),
            Product(name="Ergonomic Office Chair", category="Furniture", description="Comfortable mesh office chair with lumbar support.",  # noqa: E501
                    price=250.00, image_url="https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&q=80"),
            Product(name="Standing Desk", category="Furniture", description="Adjustable height electric standing desk for home office.",  # noqa: E501
                    price=450.00, image_url="https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=500&q=80"),
            Product(name="Men's Running Shoes", category="Apparel", description="Lightweight and breathable running shoes for daily workouts.",  # noqa: E501
                    price=120.00, image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80"),
            Product(name="Women's Yoga Pants", category="Apparel", description="High-waisted, stretchy yoga pants for fitness and casual wear.",  # noqa: E501
                    price=60.00, image_url="https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500&q=80"),
            Product(name="Stainless Steel Water Bottle", category="Accessories", description="Insulated water bottle that keeps drinks cold for 24 hours.",  # noqa: E501
                    price=30.00, image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80"),
            Product(name="Smart Watch Series 5", category="Electronics", description="Fitness tracker and smartwatch with heart rate monitor.",  # noqa: E501
                    price=299.99, image_url="https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"),
            Product(name="Mechanical Keyboard", category="Electronics", description="RGB mechanical gaming keyboard with tactile switches.",  # noqa: E501
                    price=150.00, image_url="https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80"),
            Product(name="Leather Wallet", category="Accessories", description="Genuine leather bifold wallet with RFID blocking.",  # noqa: E501
                    price=45.00, image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&q=80"),
        ]
        for p in products:
            p.features_text = f"{p.name} {p.category} {p.description}"
            db.session.add(p)
        db.session.commit()
        print(f"[+] Seeded {len(products)} products")

        # ── Users ──
        users = []
        for name in ["alice", "bob", "charlie", "diana", "eve"]:
            u = User(username=name)
            u.set_password("password123")
            db.session.add(u)
            users.append(u)
        db.session.commit()
        print(f"[+] Seeded {len(users)} users")

        # ── User Behaviors (spread over the last 14 days) ──
        action_types = ["view", "view", "view", "add_to_cart", "purchase"]  # weighted toward views
        behaviors_count = 0
        base_date = datetime.utcnow() - timedelta(days=14)

        for day_offset in range(15):
            day = base_date + timedelta(days=day_offset)
            # More activity on recent days
            n_events = random.randint(5, 15) + day_offset
            for _ in range(n_events):
                b = UserBehavior(
                    user_id=random.choice(users).id,
                    product_id=random.choice(products).id,
                    action_type=random.choice(action_types),
                    timestamp=day + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                )
                db.session.add(b)
                behaviors_count += 1
        db.session.commit()
        print(f"[+] Seeded {behaviors_count} behavior events")

        # ── Reviews ──
        reviews_count = 0
        for u in users:
            # Each user reviews 3-6 random products
            reviewed_products = random.sample(products, random.randint(3, 6))
            for p in reviewed_products:
                r = Review(
                    user_id=u.id,
                    product_id=p.id,
                    rating=random.randint(2, 5),
                    review_text=random.choice([
                        "Excellent quality, highly recommend!",
                        "Good value for the price.",
                        "Decent product, met my expectations.",
                        "Could be better, but works fine.",
                        "Amazing! Exceeded all expectations.",
                        "Solid build, fast shipping.",
                        None,  # some reviews have no text
                    ])
                )
                db.session.add(r)
                reviews_count += 1
        db.session.commit()
        print(f"[+] Seeded {reviews_count} reviews")

        print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    seed()
