from flask import Flask, render_template, request, jsonify, redirect, url_for
from chat import get_response  # Import the chatbot response logic
from offline import text_to_speech  # Import the text-to-speech function
import threading
app = Flask(__name__)

# User credentials storage
users_db = {
    "mohamedsabry": "1111",  # Example user credentials
    "admin": "1234"
}

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate user credentials
        if username in users_db and users_db[username] == password:
            return redirect(url_for("index_get"))
        else:
            error_message = "Invalid username or password. Please try again."

    return render_template("login.html", error_message=error_message)

# Account creation page
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    error_message = None

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate and add user
        if first_name and last_name and email and password:
            username = email.split('@')[0]
            if username in users_db:
                error_message = "Username already exists. Please choose another one."
            else:
                users_db[username] = password
                return redirect(url_for("login"))
        else:
            error_message = "All fields are required. Please fill them all."

    return render_template("create_account.html", error_message=error_message)

# Bot page
@app.route("/")
def index_get():
    return render_template("base.html")

# Chatbot prediction route
@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    if not text:
        return jsonify({"error": "No message provided"}), 400

    # Generate the chatbot response
    response = get_response(text)

    # Run text-to-speech in a separate thread
    speech_thread =threading.Thread(target=text_to_speech, args=(response,))
    speech_thread.start()

    # Send the response to the frontend
    return jsonify({"answer": response})


if __name__ == "__main__":
    app.run(debug=True)