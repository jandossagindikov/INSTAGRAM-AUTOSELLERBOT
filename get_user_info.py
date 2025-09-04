from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "my_verify_token"

# 1. Verification endpoint
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Forbidden", 403
    return "Error", 400

# 2. Messages/Comments listener
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 New Event:", data, flush=True)

    # Misol uchun DM xabarlar
    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for msg in entry["messaging"]:
                    print("Message:", msg)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
