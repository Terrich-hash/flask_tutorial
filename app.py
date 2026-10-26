"""
from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data.json"
)

@app.route("/api", methods=["GET"])
def get_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return jsonify(data)

    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in data file"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
"""


import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URl")

if not mongo_uri:
    raise RuntimeError("MONGO_URI is missing from the .env file")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = client["flask_database"]
collection = db["submissions"]
todo_db = client["todo_database"]
todo_collection = todo_db["todo_items"]


@app.route("/", methods=["GET", "POST"])
def form():
    error = None
    name = ""
    email = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            error = "Name and email are required."
        else:
            try:
                collection.insert_one({
                    "name": name,
                    "email": email
                })

                return redirect(url_for("success"))

            except PyMongoError:
                app.logger.exception("MongoDB insertion failed")
                error = (
                    "Unable to submit data. "
                    "Please check the database connection and try again."
                )

    return render_template(
        "form.html",
        error=error,
        name=name,
        email=email
    ), 400 if error else 200


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    item_name = request.form.get("itemName")
    item_description = request.form.get("itemDescription")

    if not item_name or not item_description:
        return jsonify({"error": "Both fields are required"}), 400

    result = todo_collection.insert_one({
        "itemName": item_name,
        "itemDescription": item_description
    })

    return jsonify({
        "message": "To-Do item submitted successfully",
        "id": str(result.inserted_id)
    }), 201

@app.route("/exit")
def exit() :
    return "thank you for visting"


if __name__ == "__main__":
    app.run(debug=True)
