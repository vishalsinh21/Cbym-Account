from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"

DB_NAME = "database.db"

# ---------- Initialize DB ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )""")
    
    # Contributors table
    cursor.execute("""CREATE TABLE IF NOT EXISTS contributors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        amount REAL,
        payment_method TEXT
    )""")
    
    # Expenses table
    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        amount REAL
    )""")
    
    # Add default admin if missing
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users(username,password) VALUES('admin','admin')")
    
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------

# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully")
    return redirect(url_for("login"))

# Change password
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        old_pass = request.form["old_password"]
        new_pass = request.form["new_password"]
        confirm_pass = request.form["confirm_password"]
        if new_pass != confirm_pass:
            flash("New passwords do not match")
        else:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (session["username"], old_pass))
            user = cursor.fetchone()
            if user:
                cursor.execute("UPDATE users SET password=? WHERE username=?", (new_pass, session["username"]))
                conn.commit()
                conn.close()
                flash("Password changed successfully")
            else:
                conn.close()
                flash("Old password is incorrect")
    return render_template("change_password.html")

# Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        # Contributors actions
        if "add" in request.form:
            name = request.form["name"]
            email = request.form["email"]
            try:
                amount = float(request.form["amount"])
            except:
                amount = 0
            payment = request.form["payment"]
            cursor.execute("INSERT INTO contributors(name,email,amount,payment_method) VALUES(?,?,?,?)",
                           (name,email,amount,payment))
            conn.commit()
        elif "edit" in request.form:
            cid = request.form["id"]
            name = request.form["name"]
            email = request.form["email"]
            try:
                amount = float(request.form["amount"])
            except:
                amount = 0
            payment = request.form["payment"]
            cursor.execute("UPDATE contributors SET name=?, email=?, amount=?, payment_method=? WHERE id=?",
                           (name,email,amount,payment,cid))
            conn.commit()
        elif "delete" in request.form:
            cid = request.form["id"]
            cursor.execute("DELETE FROM contributors WHERE id=?", (cid,))
            conn.commit()

        # Expenses actions
        if "add_expense" in request.form:
            title = request.form["title"]
            try:
                amount = float(request.form["expense_amount"])
            except:
                amount = 0
            cursor.execute("INSERT INTO expenses(title,amount) VALUES(?,?)", (title, amount))
            conn.commit()
        elif "delete_expense" in request.form:
            exp_id = request.form["expense_id"]
            cursor.execute("DELETE FROM expenses WHERE id=?", (exp_id,))
            conn.commit()

    # Fetch contributors
    cursor.execute("SELECT * FROM contributors")
    contributors = cursor.fetchall()
    total_donations = sum([row[3] for row in contributors])

    # Fetch expenses
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    total_expenses = sum([row[2] for row in expenses])

    available_balance = total_donations - total_expenses
    conn.close()

    return render_template("dashboard.html",
                           contributors=contributors,
                           expenses=expenses,
                           total_donations=total_donations,
                           total_expenses=total_expenses,
                           available_balance=available_balance)

# Public view
@app.route("/public")
def public_view():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contributors")
    contributors = cursor.fetchall()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    total_donations = sum([row[3] for row in contributors])
    total_expenses = sum([row[2] for row in expenses])
    available_balance = total_donations - total_expenses
    conn.close()
    return render_template("public.html",
                           contributors=contributors,
                           expenses=expenses,
                           total_donations=total_donations,
                           total_expenses=total_expenses,
                           available_balance=available_balance)

if __name__ == "__main__":
    app.run(debug=True)
