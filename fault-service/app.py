from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Load the trained model if it exists; fall back to a simple rule if not
MODEL_PATH = "fault_model.joblib"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    required_fields = ["lux", "v_out", "temp", "predicted_current", "measured_current", "error"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    if model is not None:
        X = pd.DataFrame([{k: data[k] for k in required_fields}])
        pred = model.predict(X)[0]
    else:
        # Fallback rule-based logic if no trained model is present yet
        pred = "FAULT" if data["error"] > 0.05 else "OK"

    return jsonify({"predicted_status": pred})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
