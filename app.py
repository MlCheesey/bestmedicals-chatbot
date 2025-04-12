import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can talk to this backend

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"

def load_inventory():
    with open("inventory.json", "r") as f:
        return json.load(f)

def format_inventory(inventory):
    info = "Here is the current inventory:\n"
    for item in inventory:
        status = "Available" if item["available"] else "Out of Stock"
        info += f"- {item['name']} (₹{item['price']}): {status}\n"
    return info

def ask_ai(full_prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a pharmacy assistant. ONLY report exact inventory numbers. Never make up stock quantities."
            },
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    }

    try:
        res = requests.post(API_URL, headers=headers, json=payload)
        data = res.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        return "⚠️ Error getting response"
    except Exception as e:
        return f"❌ Error talking to server: {str(e)}"

def build_prompt(user_input, inventory):
    inventory_info = format_inventory(inventory)
    prompt = (
        "The customer is asking about pharmacy items."
        " You have access to the inventory and must answer in full, friendly sentences. Never tell the customer that you're an AI but that you're the personal assistant of Best Medicals The best pharmacy located in Stadium Complex in Kannur. Don't disclose everything with the user unless they ask for it except for the medicine in stock and is available and the price. Don't disclose unless the user asks: The phone number is +91 7073777755 and the website is bestmedicals.in. If the user says that they want or want to buy medicine tell them to call or visit the phone number or website."
        " Be smart and detailed.\n\n"
        f"Inventory:\n{inventory_info}\n"
        f"Customer: {user_input}\n"
        "Your reply:"
    )
    return prompt

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"response": "Please provide a message."}), 400

    try:
        inventory = load_inventory()
        full_prompt = build_prompt(user_input, inventory)
        reply = ask_ai(full_prompt)
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"⚠️ Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
