from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import random
import os
import time
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Flask-Mail configuration for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'smoulaiah5@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'ddxh mrqpcgvq ojrg'  # Replace with your email password
mail = Mail(app)

# In-memory OTP storage (you can use a database in production)
otp_dict = {}

# File to store user links
LINKS_FILE = 'user_links.json'

# Load existing links from the JSON file
def load_links():
    # Check if the file exists
    if os.path.exists(LINKS_FILE):
        try:
            with open(LINKS_FILE, 'r') as f:
                links_data = json.load(f)  # Load the JSON content
                return links_data
        except json.JSONDecodeError:
            # If the JSON is invalid or file is empty, return an empty dictionary
            return {}
    return {}  # Return an empty dictionary if the file doesn't exist

# Save links to the JSON file
def save_links(links_data):
    with open(LINKS_FILE, 'w') as f:
        json.dump(links_data, f, indent=4)  # Save with indentation for readability

# Route to render login page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_dict[email] = {'otp': otp, 'time': time.time()}

        # Send OTP via email
        msg = Message("Your OTP Code", sender="smoulaiah5@gmail.com", recipients=[email])
        msg.body = f"Your OTP code is {otp}"
        mail.send(msg)

        return redirect(url_for("verify", email=email))

    return render_template("login.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    email = request.args.get("email")
    if request.method == "POST":
        otp = int(request.form.get("otp"))
        # Check OTP validity
        if email in otp_dict:
            stored_otp = otp_dict[email]['otp']
            otp_time = otp_dict[email]['time']

            if otp == stored_otp and time.time() - otp_time < 300:  # OTP expires after 5 minutes
                session['user'] = email  # Mark user as logged in
                # Remove OTP after successful verification
                del otp_dict[email]
                return redirect(url_for("add_links"))
            else:
                # Remove expired OTP
                del otp_dict[email]
                return "Invalid or expired OTP", 400
        else:
            return "OTP not sent or expired", 400

    return render_template("verify.html", email=email)

# Route to allow the user to add and view links
@app.route("/add_links", methods=["GET", "POST"])
def add_links():
    if 'user' not in session:
        return redirect(url_for('index'))

    email = session['user']

    # Load the links data from the file
    links_data = load_links()

    # Initialize a list for the user's links if not already present
    if email not in links_data:
        links_data[email] = {'links': []}  # Create an entry for the user

    if request.method == "POST":
        new_link = request.form.get("link")
        description = request.form.get("description")

        if new_link and description:
            # Check if the link already exists for the user
            existing_links = links_data[email]['links']
            if not any(link['url'] == new_link for link in existing_links):
                # Add the new link and description to the list
                links_data[email]['links'].append({'url': new_link, 'description': description})
                save_links(links_data)  # Save the updated links to the file
            else:
                return "Duplicate link! This link has already been added.", 400

    # Render the page to add/view links
    return render_template("add_links.html", email=email, links=links_data[email]['links'])

# Route to redirect to Google Drive after adding links
@app.route("/go_to_drive")
def go_to_drive():
    if 'user' not in session:
        return redirect(url_for('index'))
    # Redirect to Google Drive link
    return redirect("https://drive.google.com/drive/folders/1sQnk6YW5gfsnrE__X5LdMKB_8jn6iXZ9")

if __name__ == "__main__":
    app.run(debug=True)
