from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required to use sessions
CORS(app)  # Allow cross-origin requests (useful if frontend is separate)

# Home route
@app.route("/")
def home():
    return render_template("chat2.html")

# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please enter a message."}), 400

    # Initialize chat history in session if not exists
    if "history" not in session:
        session["history"] = []

    # Append the new user message
    session["history"].append(f"User: {user_input}")

    # Combine chat history for the prompt
    history_prompt = "\n".join(session["history"]) + "\nPhilosopher:"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1",
            "prompt": history_prompt,
            "stream": False
        }, timeout=30)

        if response.status_code == 200:
            data = response.json()
            reply = data["response"].strip()

            # Save the AI's reply to history
            session["history"].append(f"Philosopher: {reply}")
            session.modified = True  # Ensure session is updated

            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "Sorry, I couldn't reach the philosophical mind right now."})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

# Reset conversation history
@app.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"message": "Conversation history cleared."})

if __name__ == "__main__":
    app.run(debug=True)
