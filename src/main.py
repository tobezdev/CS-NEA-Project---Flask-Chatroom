from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime
import sqlite3


# Helper function for input sanitization
def sanitize_input(_input):
    # Remove any SQL meta-characters and limit length to 256 chars.
    return re.sub(r"[^a-zA-Z0-9_@.\-:() ]", "", str(_input))[:256]


app = Flask(__name__)
app.config["SECRET_KEY"] = "yippeee_a_very_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Database Models
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    channels = db.relationship("Channel", backref="group", lazy=True)


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupid = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    slowmode = db.Column(db.Integer, default=0)
    messages = db.relationship("Message", backref="channel", lazy=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    displayname = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(256))
    profile_image = db.Column(db.String(256))
    messages_sent = db.relationship(
        "Message", backref="sender", lazy=True, foreign_keys="Message.senderid"
    )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    senderid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipientid = db.Column(db.Integer, nullable=False)  # user or channel id
    datetime = db.Column(db.String(64), default=lambda: datetime.utcnow().isoformat())
    content = db.Column(db.String(1024), nullable=False)


def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        displayname TEXT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        bio TEXT,
        profile_image TEXT
    )""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS group (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    c.execute("""CREATE TABLE IF NOT EXISTS channel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        groupid INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        slowmode INTEGER DEFAULT 0,
        FOREIGN KEY(groupid) REFERENCES group(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        senderid INTEGER NOT NULL,
        recipientid INTEGER NOT NULL,
        datetime TEXT,
        content TEXT NOT NULL,
        FOREIGN KEY(senderid) REFERENCES user(id)
    )""")
    conn.commit()
    conn.close()


# Placeholder for routes and chat logic
@app.route("/")
def index():
    return render_template("chatroom.html")


@app.route("/send", methods=["POST"])
def send_message():
    message = sanitize_input(request.form.get("message", ""))
    user_id = session.get("user_id", 1)  # Placeholder for user session
    # Command handling
    if message.startswith("$"):
        command, *args = message[1:].split(" ", 1)
        command = command.lower()
        if command == "help":
            help_text = """
            $help - shows this help message
            $swapchannel <id> - swap to the channel with the provided id
            $whisper <user> <message> - send a whisper to another user
            $account - go to your account page
            $silent <message> - send a silent message
            $setslowmode <duration> - set the current channel's slowmode
            """
            flash(help_text, "info")
            return redirect(url_for("index"))
        elif command == "swapchannel" and args:
            channel_id = sanitize_input(args[0])
            # Logic to swap channel (not implemented)
            flash(f"Swapped to channel {channel_id}", "info")
            return redirect(url_for("index"))
        elif command == "whisper" and args:
            whisper_args = args[0].split(" ", 1)
            target_user = sanitize_input(whisper_args[0])
            whisper_message = whisper_args[1] if len(whisper_args) > 1 else None
            # Logic to send whisper (not implemented)
            flash(f"Whispered to {target_user}", "info")
            return redirect(url_for("index"))
        elif command == "account":
            return redirect(url_for("account"))
        elif command == "silent" and args:
            silent_message = sanitize_input(args[0])
            # Logic to send silent message (not implemented)
            flash("Silent message sent.", "info")
            return redirect(url_for("index"))
        elif command == "setslowmode" and args:
            duration = sanitize_input(args[0])
            # Logic to set slowmode (not implemented)
            flash(f"Slowmode set to {duration} seconds.", "info")
            return redirect(url_for("index"))
        else:
            flash("Unknown command or missing arguments.", "error")
            return redirect(url_for("index"))
    # Regular message
    new_msg = Message(
        senderid=user_id, recipientid=1, content=message
    )  # recipientid=1 placeholder
    db.session.add(new_msg)
    db.session.commit()
    flash("Message sent!", "success")
    return redirect(url_for("index"))


@app.route("/account", methods=["GET", "POST"])
def account():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to access your account.", "error")
        return redirect(url_for("login"))
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        displayname = sanitize_input(request.form.get("displayname", ""))
        email = sanitize_input(request.form.get("email", ""))
        bio = sanitize_input(request.form.get("bio", ""))
        profile_image = sanitize_input(request.form.get("profile_image", ""))
        c.execute(
            """UPDATE user SET username=?, displayname=?, email=?, bio=?, profile_image=? WHERE id=?""",
            (username, displayname, email, bio, profile_image, user_id),
        )
        conn.commit()
        flash("Account updated!", "success")
    c.execute(
        "SELECT username, displayname, email, bio, profile_image FROM user WHERE id=?",
        (user_id,),
    )
    user = c.fetchone()
    conn.close()
    return render_template("account.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        password = request.form.get("password", "")
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("SELECT id, password_hash FROM user WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        email = sanitize_input(request.form.get("email", ""))
        password = request.form.get("password", "")
        password_hash = generate_password_hash(password)
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "error")
        finally:
            conn.close()
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    # Create the database tables within the context of the current running app.
    with app.app_context():
        db.create_all()

    # Initialise the SQLite DB as a .db plainfile.
    init_db()

    # Run the app in debug mode (for testing) on localhost:5500.
    app.run(debug=True, port=5500)
