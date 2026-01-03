import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from PIL import Image

# Configure application
app = Flask(__name__)


# Some sections of this code were written with the help of Cs50 duck debugger and chatopenai

# Configure system to save session on filesystem instead of cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Configure email system
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'ashleyprojectcs50@gmail.com'
app.config['MAIL_PASSWORD'] = 'elvd pmva fzdm tjtu'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

Session(app)

@app.after_request
def after_request(response):
    """Ensure that responses arent cached, so that the most up to data info is available"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Connect to database:
db = SQL("sqlite:///htreasures.db")

# Create users table
db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, username text UNIQUE NOT NULL, email text UNIQUE NOT NULL, hash TEXT NOT NULL)")

# Specify list of conditions
conditions = ["new", "like new", "used", "old"]

# Create items table
db.execute("CREATE TABLE IF NOT EXISTS items(item_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, user_id INTEGER NOT NULL, item text NOT NULL, condition TEXT NOT NULL, location TEXT NOT NULL, price numeric NOT NULL, files TEXT NOT NULL, description text NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")


# Define error function
def error(message):
    return render_template("error.html", message = message)


# Show all posted items when logged in
@app.route("/", methods = ["GET"])
@login_required
def index():
    if request.method =="GET":
        items = db.execute("SELECT * FROM items")
        for item in items:
            print(item["files"])
        return render_template("index.html", items = items)

# Show the seller's listings and delete from database when marked as sold
@app.route("/listings", methods=["GET","POST"])
@login_required
def listings():
    if request.method =="GET":
        listed_items = db.execute("SELECT * FROM items WHERE user_id = ?", session["user_id"])
        return render_template("listings.html", listed_items = listed_items)

    elif request.method =="POST":
       id = request.get_json()
       id = id["item_id"]
       db.execute("DELETE FROM items WHERE item_id = ?", id)
       listed_items = db.execute("SELECT * FROM items WHERE user_id = ?", session["user_id"])
       return render_template("listings.html", listed_items = listed_items)

# Search among posts for items
@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    if q:
        items = db.execute("SELECT * FROM items WHERE item LIKE ?", "%" + q +"%")
    else:
        items = db.execute("SELECT * FROM items")
    return render_template("cards.html", items = items)

# Create specific item page
@app.route("/itemsearch", methods =["GET"])
@login_required
def item():
    if request.method =="GET":
        id = request.args.get("q")
        item = db.execute("SELECT * FROM items WHERE item_id = ?", id)
        item = item[0]
        files = item["files"].split(",")
        return render_template("item.html", item = item, files = files)

# Send email to seller
@app.route('/email', methods = ["GET", "POST"])
@login_required
def email():
    if request.method == "GET":
        id = event.target.getAttribute("data-item");
        id = id["item_id"]
        item = db.execute("SELECT item FROM items WHERE item_id = ?", id)
        item = item[0]["item"]
        return render_template("item.html", item = item)

    elif request.method == "POST":
        # Get item and item id from requested item
        id = request.get_json()
        id = id["item_id"]
        item = db.execute("SELECT item,files FROM items WHERE item_id = ?", id)
        pic = item[0]["files"]
        first_image = pic.split(',')[0]
        item = item[0]["item"]


        # Get user id of seller from item
        user_id = db.execute("SELECT user_id FROM items WHERE item_id = ?", id)
        user_id = user_id[0]["user_id"]
        # Get email address of seller
        seller_email = db.execute("SELECT email FROM users WHERE id = ?", user_id)
        seller_email = seller_email[0]["email"]

        # Get email address of buyer
        buyer_email = db.execute("SELECT email FROM users WHERE id = ?", session["user_id"])
        buyer_email = buyer_email[0]["email"]
        print(buyer_email)
        print(app.config['MAIL_USERNAME'])
        msg= Message(
            subject='Potential Buyer',
            sender = app.config['MAIL_USERNAME'],
            recipients = [seller_email],
            reply_to = "[seller_email],[buyer_email]")

        msg.html = f"""
        <html>
            <body>

                <p>A buyer is potentially interested in the {item }. Is it still available?</p>
                <img src = "cid:image1">
                <p>Reply to buyer in email.</p>

            </body>
        </html>

        """
        # Attach image- written with the help of C50 debugger
        file_path = os.path.join('static',first_image)
        with app.open_resource(file_path) as fp:
            msg.attach(file_path,"image/jpeg", fp.read(), headers ={'Content-ID': '<image1>'})

        #msg.body = f"A buyer is potentially interested in the {item}. Is it still available? Reply to buyer in email"
        mail.send(msg)
        return render_template("item.html", item = item)

# Allow users to post items for sale
@app.route("/sell", methods = ["GET","POST"])
@login_required
def sell():
    if request.method =="GET":
        return render_template("sell.html", conditions = conditions)

    elif request.method =="POST":
        item = request.form.get("item")
        condition = request.form.get("condition")
        description = request.form.get("description")
        location = request.form.get("location")

        if not item or not condition or not description or not location:
            return error("Missing field")

        files = request.files.getlist("files")

        if not files or all(file.filename == '' for file in files):
            return error("Missing picture")

        try:
            price = float(request.form.get("price"))

        except ValueError:
            return error("Insert a valid price")

        else:
            # Save files submitted in the database- written with the help of Cs50 debugger and chatopenai
            file_path = []
            upload_dir = os.path.join("static","uploads")
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                if file and file.filename:
                    try:
                        print(f"Processing: {file.filename}")
                        image = Image.open(file)


                        image.thumbnail((256, 256) , resample = Image.LANCZOS)


                        f_path = os.path.join(upload_dir, file.filename)
                        image.save(f_path)

                        print(f"Saved resized image to: {f_path}")

                        file_path.append(os.path.join("uploads", file.filename))

                    except Exception as e:
                        print(f"Error processing file {file.filename}: {e}")

            # Join file paths to store in DB
            all_file_paths = ",".join(file_path)

            db.execute("INSERT INTO items(user_id, item, condition, location, price, files, description) VALUES (?,?,?,?,?,?,?)", session["user_id"],item, condition, location, price, all_file_paths, description )

            return redirect("/")


# Register new user
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    elif request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        if not username or not email or not password or not confirmation:
            return error("Missing field entry")

        if password != confirmation:
            return error("Password fields do not match")

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users(username,email, hash) VALUES(?,?,?)", username, email, hash)

        except ValueError:

            return("Username already exists")

        else:
            return render_template("login.html")

@app.route("/login", methods =["GET","POST"])
def login():
    # Forget previously submitted username
    session.clear()

    if request.method =="GET":
        return render_template("login.html")

    elif request.method =="POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure that there is no missing username or password
        if not username or not password:
             return error("Missing field")

        # Pull password info and username from database
        userinfo = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure password and username matches and that there is a username
        if len(userinfo) != 1 or not check_password_hash(userinfo[0]["hash"], password):
               return error("Invalid username or username password combination")

        # Save user id in session
        session["user_id"] = userinfo[0]["id"]


        return redirect("/")



