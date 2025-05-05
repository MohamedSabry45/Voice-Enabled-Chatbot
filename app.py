from flask import Flask, render_template, request, jsonify
from chat import get_response
from offline import text_to_speech
import threading

app = Flask(__name__)

@app.route("/")
def index_get():
    return render_template("base.html")

@app.post("/predict")
def predict():
    data = request.get_json()
    
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    text = data["message"]
    response = get_response(text)

    if response is False:
        # أمر مسح المحادثة
        return jsonify({"answer": "__CLEAR__"})

    if not response or response.strip() == "":
        response = "عذرًا، لم أفهم سؤالك. من فضلك حاول مرة أخرى."

    if data.get("agentResponseMode") == 'voice':
        try:
            if not engine._inLoop:  # type: ignore
                threading.Thread(target=text_to_speech, args=(response,)).start()
        except Exception as e:
            print("Error in voice response:", e)

    return jsonify({"answer": response})

if __name__ == "__main__":
    app.run(debug=True)
