from flask import Flask, render_template, jsonify
from routes.monitor import monitor_bp
from routes.attenuation import attenuation_bp
from routes.privacy import privacy_bp   # <--- הוספנו את זה!
from routes.analytics import analytics_bp

app = Flask(__name__)

app.register_blueprint(monitor_bp)
app.register_blueprint(attenuation_bp)
app.register_blueprint(privacy_bp)      # <--- והוספנו את זה!
app.register_blueprint(analytics_bp)

@app.route('/')
def main_dashboard():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({"status": "Healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)