from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Social Media Analytics Dashboard",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api": "/api/analytics"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/analytics')
def analytics():
    return jsonify({
        "total_posts": 0,
        "sentiment": {"positive": 0, "neutral": 0, "negative": 0}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
