import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

# UPLOAD CONFIG
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DB CONFIG
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------
# MODELS
# ------------------------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    image = db.Column(db.String(200))   # NEW


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    address = db.Column(db.String(300))   # NEW


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))


# ------------------------
# HOME
# ------------------------
@app.route("/")
def home():
    return redirect("/login")


# ------------------------
# LOGIN
# ------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            session['user'] = user.name
            session['role'] = user.role

            return redirect("/dashboard" if user.role == "admin" else "/customer")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ------------------------
# SIGNUP
# ------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role="customer"
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("signup.html")


# ------------------------
# LOGOUT
# ------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------------
# DASHBOARD (ADMIN)
# ------------------------
@app.route("/dashboard")
def dashboard():
    if session.get('role') != 'admin':
        return redirect("/login")

    products = Product.query.all()

    return render_template("dashboard.html",
                           total_products=len(products),
                           total_stock=sum([p.stock for p in products]))


# ------------------------
# PRODUCTS (ADMIN)
# ------------------------
@app.route("/products")
def products():
    if session.get('role') != 'admin':
        return redirect("/login")

    return render_template("products.html",
                           products=Product.query.all(),
                           categories=Category.query.all())


@app.route("/add_product", methods=["POST"])
def add_product():
    file = request.files['image']
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    product = Product(
        name=request.form['name'],
        category=request.form['category'],
        supplier=request.form['supplier'],
        price=float(request.form['price']),
        stock=int(request.form['stock']),
        image=filename
    )

    db.session.add(product)
    db.session.commit()
    return redirect("/products")


@app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/products")


# ------------------------
# CATEGORY
# ------------------------
@app.route("/categories")
def categories():
    return render_template("categories.html", categories=Category.query.all())


@app.route("/add_category", methods=["POST"])
def add_category():
    db.session.add(Category(
        name=request.form['name'],
        description=request.form['description']
    ))
    db.session.commit()
    return redirect("/categories")


@app.route("/delete_category/<int:id>")
def delete_category(id):
    db.session.delete(Category.query.get(id))
    db.session.commit()
    return redirect("/categories")


# ------------------------
# SUPPLIER
# ------------------------
@app.route("/suppliers")
def suppliers():
    return render_template("suppliers.html", suppliers=Supplier.query.all())


@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    db.session.add(Supplier(
        name=request.form['name'],
        contact=request.form['contact']
    ))
    db.session.commit()
    return redirect("/suppliers")


@app.route("/delete_supplier/<int:id>")
def delete_supplier(id):
    db.session.delete(Supplier.query.get(id))
    db.session.commit()
    return redirect("/suppliers")


# ------------------------
# CUSTOMER PANEL
# ------------------------
@app.route("/customer")
def customer():
    return render_template("customer.html", products=Product.query.all())


@app.route("/order/<int:id>", methods=["POST"])
def place_order(id):
    product = Product.query.get(id)
    qty = int(request.form['qty'])
    address = request.form['address']

    if qty > product.stock:
        return "Not enough stock"

    product.stock -= qty

    db.session.add(Order(
        product_id=id,
        quantity=qty,
        address=address
    ))

    db.session.commit()
    return redirect("/customer")


# ------------------------
# ORDERS (ADMIN)
# ------------------------
@app.route("/orders")
def orders():
    orders = Order.query.all()
    product_map = {p.id: p.name for p in Product.query.all()}

    return render_template("orders.html",
                           orders=orders,
                           product_map=product_map)


# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)