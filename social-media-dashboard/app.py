from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Social Media Analytics Dashboard API", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Use port 5001 instead of 5000 to avoid macOS AirPlay conflict
    app.run(debug=True, host='127.0.0.1', port=5001)
