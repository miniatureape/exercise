from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask.ext import pymongo
import Users

app = Flask('goal')
app.debug = True
mongo = pymongo.PyMongo(app)

Users.setApp(app)
Users.setDb(mongo)

@app.route("/user/<user_id>/deposit/<int:amount>", methods=['POST'])
def deposit(user_id, amount):

    user = Users.find_by_id(user_id)

    if user:
        Users.deposit(user, amount, request.form.get('date'))

    return redirect('/user/%s/excercises' % user_id)

@app.route("/user/<user_id>/excercise/<eid>/delete", methods=['POST'])
def del_excercise(user_id, eid):

    user = Users.find_by_id(user_id)

    if user:
        Users.del_excercise(user, eid)

    return redirect('/user/%s/excercises' % user_id)

@app.route("/user/<user_id>/excercises", methods=['GET', 'POST'])
def excercises(user_id):

    user = Users.find_by_id(user_id)

    if request.method == 'POST':
        eid = request.form.get('eid', None)

        data = {
            "name": request.form.get('name', 'Untitled'),
            "value": int(request.form.get('value', 0)),
        }

        user = Users.set_excercise(user, data, eid)

    return render_template('excercises.html', user=user)

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        email = request.form['email']
        user = Users.find_one({'email': email})
        if not user:
            print "creating new user"
            user_id = Users.create(email)
            return redirect('/user/%s/excercises?add=1' % user_id)
        else:
            "email already registered"
            pass

    return render_template('index.html')

if __name__ == "__main__":
    app.run()
