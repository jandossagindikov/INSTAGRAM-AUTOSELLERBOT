from flask import Flask, request, render_template

app = Flask(__name__)

VERIFY_TOKEN = "myverifytoken123"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')  # 👈 Yangi route qo‘shildi

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK VERIFIED ✅")
            return challenge, 200
        else:
            return "Verification failed", 403

    if request.method == 'POST':
        print("Webhook event received:", request.json)
        return "OK", 200

@app.route('/deauth', methods=['POST'])
def deauth():
    print("DEAUTH received:", request.json)
    return "OK", 200

@app.route('/delete', methods=['POST'])
def delete():
    print("DELETE request received:", request.json)
    return "User data deleted", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
