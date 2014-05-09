from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import jsonify
from flask.ext import pymongo
from bson import json_util
import json
import Users

app = Flask('goal')
app.debug = True
mongo = pymongo.PyMongo(app)

Users.setApp(app)
Users.setDb(mongo)

def jsonifym(d):
    "jsonifier that works with mongo objects"
    return json.dumps(d, default=json_util.default)


@app.route("/user/<user_id>/deposit/<int:amount>", methods=['POST'])
def deposit(user_id, amount):

    user = Users.find_by_id(user_id)

    if user:
        Users.deposit(user, amount, request.form.get('date'))

    if request.is_xhr:
       return jsonifym(user)

    return redirect('/user/%s/exercises' % user_id)

@app.route("/user/<user_id>/exercise/<eid>/delete", methods=['POST'])
def del_exercise(user_id, eid):

    user = Users.find_by_id(user_id)

    if user:
        Users.del_exercise(user, eid)

    return redirect('/user/%s/exercises' % user_id)

@app.route("/user/<user_id>/delete", methods=['GET', 'POST'])
def del_user(user_id):

    user = Users.find_by_id(user_id)
    if request.method == 'POST' and request.form.get('confirmed', '1'):
        if user:
            Users.delete(user)
        return redirect('/')

    return render_template('delete.html', user=user)

@app.route("/user/<user_id>/exercises/edit", methods=['POST'])
def edit_exercise(user_id):

    user = Users.find_by_id(user_id)
    eid = request.form.get('eid', None)

    data = {
        "name": request.form.get('name', 'Untitled'),
        "value": int(request.form.get('value', 0)),
        "quantity": int(request.form.get('quantity', 0)),
    }

    user = Users.set_exercise(user, data, eid)

    return redirect('/user/%s/exercises' % user_id)

@app.route("/user/<user_id>/exercises", methods=['GET'])
def exercises(user_id):

    user = Users.find_by_id(user_id)

    if not user:
        return redirect('/')

    return render_template('exercises.html', user=user)

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        email = request.form['email']

        if not email:
            return render_template('index.html')

        user = Users.find_one({'email': email})

        if not user:
            user_id = Users.create(email)
            return redirect('/user/%s/exercises?add=1' % user_id)
        else:
            "email already registered"
            pass

    return render_template('index.html')

if __name__ == "__main__":
    app.run()
