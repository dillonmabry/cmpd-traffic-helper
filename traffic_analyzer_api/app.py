from flask import Flask, jsonify
app = Flask(__name__)


@app.route("/api/test")
def test():
    return jsonify(response="success")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
