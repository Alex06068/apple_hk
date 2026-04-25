from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Apple 香港</h1><p>網站正在修復中，請稍後。</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
