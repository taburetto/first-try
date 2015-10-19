from flask import Flask, request, abort, jsonify
from User import check, add

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello world!"


@app.route('/api/user/check', methods=['POST'])
def check_email():
    if not request.json or not 'email' in request.json:
        abort(400)
    email = request.json.get('email')
    if check(email):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/api/user/add/')
def user_add(email):
    if not request.json or not 'email' in request.json:
        abort(400)
    email = request.json.get('email')
    add(email=email)
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run()