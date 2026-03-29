from app import app, db, Product, User

with app.app_context():
    db.create_all()

    # ------------------------
    # INSERT PRODUCTS
    # ------------------------
    if not Product.query.first():
        p1 = Product(name="Mouse", category="Tech", supplier="HP", price=500, stock=20)
        p2 = Product(name="Keyboard", category="Tech", supplier="Dell", price=800, stock=15)
        p3 = Product(name="Monitor", category="Electronics", supplier="LG", price=7000, stock=5)

        db.session.add_all([p1, p2, p3])
        print("Products inserted ✅")

    # ------------------------
    # INSERT USERS
    # ------------------------
    if not User.query.first():
        admin = User(
            name="Admin",
            email="admin@gmail.com",
            password="admin123",
            role="admin"
        )

        customer = User(
            name="Customer",
            email="user@gmail.com",
            password="user123",
            role="customer"
        )

        db.session.add_all([admin, customer])
        print("Users inserted ✅")

    db.session.commit()
    print("Database initialized successfully 🚀")