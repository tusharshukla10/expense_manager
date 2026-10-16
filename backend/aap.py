
import os
from urllib.parse import quote_plus

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, send_from_directory, session
from flask_cors import CORS
from psycopg2 import sql
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from models import db, bcrypt, User, Expense


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "frontend")
)

load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

if not DB_PASSWORD:
    raise RuntimeError("DATABASE_PASSWORD is missing from .env")

if not SECRET_KEY:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")


# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

db.init_app(app)
bcrypt.init_app(app)
CORS(app)


# ==========================================
# DATABASE SETUP
# ==========================================

def create_database_if_not_exists():
    """Create the PostgreSQL database if it does not exist."""
    connection = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    try:
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (DB_NAME,),
            )

            if cursor.fetchone():
                print(f"Database '{DB_NAME}' already exists.")
            else:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(DB_NAME)
                    )
                )
                print(f"Database '{DB_NAME}' created successfully.")
    finally:
        connection.close()


create_database_if_not_exists()

with app.app_context():
    db.create_all()
    print("Database tables are ready.")


# ==========================================
# FRONTEND PAGES
# ==========================================

print("Frontend folder:", FRONTEND_DIR)
print(
    "Registration file exists:",
    os.path.isfile(os.path.join(FRONTEND_DIR, "register.html"))
)
    

@app.route("/")
def home():
    if not session.get("user_id"):
        return redirect("/login.html")
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/register.html")
def register_page():
    return send_from_directory(FRONTEND_DIR, "register.html")


@app.route("/login.html")
def login_page():
    if session.get("user_id"):
        return redirect("/")
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/style.css")
def style():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(FRONTEND_DIR, "script.js")


# ==========================================
# REGISTER USER
# ==========================================

@app.route("/api/v1/register", methods=["POST"])
def register_user():
    """Validate registration details and create a user."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (username, email, password)
    ):
        return jsonify({
            "error": "Username, email, and password are required"
        }), 400

    username = username.strip()
    email = email.strip().lower()

    if len(username) > 80 or len(email) > 120:
        return jsonify({
            "error": "Username or email is too long"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    existing_user = User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
        return jsonify({
            "error": "Username or email already registered"
        }), 409

    user = User(username=username, email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        # Log the user into the Flask session after registration.
        session.clear()
        session["user_id"] = user.id

        return jsonify({
            "message": "Registration successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }), 201

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("User registration failed")

        return jsonify({
            "error": "Could not register user"
        }), 500


# ==========================================
# GET USER EXPENSES
# ==========================================

@app.route("/api/v1/users/<int:user_id>/expenses", methods=["GET"])
def get_user_expenses(user_id):
    if session.get("user_id") != user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    expenses = Expense.query.filter_by(user_id=user_id).all()

    return jsonify([
        expense.to_dict() for expense in expenses
    ]), 200


# ==========================================
# ADD EXPENSE
# ==========================================

@app.route("/api/v1/expenses", methods=["POST"])
def add_expense():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    title = data.get("title")
    amount = data.get("amount")
    category = data.get("category")
    user_id = session.get("user_id")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(category, str) or not category.strip():
        return jsonify({"error": "Category is required"}), 400

    if isinstance(amount, bool):
        return jsonify({"error": "Amount must be a positive number"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a positive number"}), 400

    if user_id is None:
        return jsonify({"error": "Please register first"}), 401

    expense = Expense(
        title=title.strip(),
        amount=amount,
        category=category.strip(),
        user_id=user_id,
    )

    try:
        db.session.add(expense)
        db.session.commit()

        return jsonify({
            "message": "Expense created successfully",
            "expense": expense.to_dict(),
        }), 201

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to create expense")

        return jsonify({"error": "Could not save expense"}), 500


# ==========================================
# UPDATE EXPENSE
# ==========================================

@app.route("/api/v1/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Please register first"}), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    expense = db.session.get(Expense, expense_id)

    if expense is None or expense.user_id != user_id:
        return jsonify({"error": "Expense not found"}), 404

    title = data.get("title")
    category = data.get("category")
    amount = data.get("amount")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(category, str) or not category.strip():
        return jsonify({"error": "Category is required"}), 400

    if isinstance(amount, bool):
        return jsonify({"error": "Amount must be a positive number"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a positive number"}), 400

    expense.title = title.strip()
    expense.amount = amount
    expense.category = category.strip()

    try:
        db.session.commit()

        return jsonify({
            "message": "Expense updated successfully",
            "expense": expense.to_dict(),
        }), 200

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to update expense")

        return jsonify({"error": "Could not update expense"}), 500


# ==========================================
# DELETE EXPENSE
# ==========================================

@app.route("/api/v1/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Please register first"}), 401

    expense = db.session.get(Expense, expense_id)

    if expense is None or expense.user_id != user_id:
        return jsonify({"error": "Expense not found"}), 404

    try:
        db.session.delete(expense)
        db.session.commit()

        return jsonify({
            "message": "Expense deleted successfully"
        }), 200

    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to delete expense")

        return jsonify({"error": "Could not delete expense"}), 500


# ==========================================
# USER LOGIN
# ==========================================

@app.route("/api/v1/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200

#==========================================
#LOGOUT_USER
#==========================================


@app.route("/api/v1/logout", methods=["POST"])
def logout_user():
    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200





# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
