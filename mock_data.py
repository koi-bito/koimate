from app import create_app
from models import db, Product

def init_mock_data():
    app = create_app()
    with app.app_context():
        # Clear existing
        db.drop_all()
        db.create_all()

        products = [
            Product(name="Smartphone X1", category="Electronics", description="Latest model smartphone with OLED display and advanced camera.", price=999.99, image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80"),
            Product(name="Wireless Earbuds Pro", category="Electronics", description="Noise-cancelling wireless earbuds with 24-hour battery life.", price=199.99, image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80"),
            Product(name="Ergonomic Office Chair", category="Furniture", description="Comfortable mesh office chair with lumbar support.", price=250.00, image_url="https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&q=80"),
            Product(name="Standing Desk", category="Furniture", description="Adjustable height electric standing desk for home office.", price=450.00, image_url="https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=500&q=80"),
            Product(name="Men's Running Shoes", category="Apparel", description="Lightweight and breathable running shoes for daily workouts.", price=120.00, image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80"),
            Product(name="Women's Yoga Pants", category="Apparel", description="High-waisted, stretchy yoga pants for fitness and casual wear.", price=60.00, image_url="https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500&q=80"),
            Product(name="Stainless Steel Water Bottle", category="Accessories", description="Insulated water bottle that keeps drinks cold for 24 hours.", price=30.00, image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80"),
            Product(name="Smart Watch Series 5", category="Electronics", description="Fitness tracker and smartwatch with heart rate monitor.", price=299.99, image_url="https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"),
            Product(name="Mechanical Keyboard", category="Electronics", description="RGB mechanical gaming keyboard with tactile switches.", price=150.00, image_url="https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80"),
            Product(name="Leather Wallet", category="Accessories", description="Genuine leather bifold wallet with RFID blocking.", price=45.00, image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&q=80"),
        ]

        for p in products:
            p.features_text = f"{p.name} {p.category} {p.description}"
            db.session.add(p)
            
        db.session.commit()
        print("Mock data initialized successfully!")

if __name__ == '__main__':
    init_mock_data()
