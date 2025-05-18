from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for sessions
CORS(app)

# 👤 Define personality
SYSTEM_PERSONALITY = (
    "You are Aurelius, a modern-day Stoic philosopher with a calm and thoughtful tone.\n"
    "You value wisdom, logic, and virtue. You speak clearly and patiently, often reflecting on ancient philosophy.\n"
    "Draw inspiration from Marcus Aurelius, Epictetus, and Seneca. Do not rush answers.\n"
)

# Home route
@app.route("/")
def home():
    return render_template("chat2.html")

# Chat route with personality and memory
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please enter a message."}), 400

    # Initialize conversation history
    if "history" not in session:
        session["history"] = []

    session["history"].append(f"User: {user_input}")

    # Combine personality and history for the prompt
    prompt = SYSTEM_PERSONALITY + "\n" + "\n".join(session["history"]) + "\nPhilosopher:"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1",  # Make sure this model is correct and available
            "prompt": prompt,
            "stream": False
        }, timeout=30)

        if response.status_code == 200:
            data = response.json()
            reply = data["response"].strip()

            # Save the AI's reply
            session["history"].append(f"Philosopher: {reply}")
            session.modified = True

            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "Sorry, I couldn't reach the philosophical mind right now."})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

# Reset conversation
@app.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"message": "Conversation history cleared."})

if __name__ == "__main__":
    app.run(debug=True)
