from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import jsonify
from flask import flash
from flask.ext import pymongo
from bson import json_util
import os
import json
import Users
import sendgrid

app = Flask('goal')
app.config.from_envvar('EXERCISE_APP_SETTINGS')
mongo = pymongo.PyMongo(app)

Users.setApp(app)
Users.setDb(mongo)

def flash_list(flashes, category):
    for item in flashes:
        flash(item, category)

def jsonifym(d):
    "jsonifier that works with mongo objects"
    return json.dumps(d, default=json_util.default)


@app.route("/user/<user_id>/deposit/<int:amount>", methods=['POST'])
@app.route("/user/<user_id>/deposit", methods=['POST'], defaults={'amount': None})
def deposit(user_id, amount):

    user = Users.find_by_id(user_id)
    eid = request.form.get('eid', None)
    exercise = None

    if not amount:
        amount = int(request.form.get('amount'))

    if user and eid:
        exercise = Users.find_exercise(user, eid)

    if user:
        Users.deposit(user, amount, exercise, request.form.get('date'))
    else:
        if request.is_xhr:
            return jsonifym({error: 'Could not find user'})
        else:
            return redirect('/user/%s/exercises' % user_id)

    if request.is_xhr:
       return jsonifym(user)

    return redirect('/user/%s/exercises' % user_id)

@app.route("/user/<user_id>/exercise/<eid>/delete", methods=['POST'])
def del_exercise(user_id, eid):

    user = Users.find_by_id(user_id)

    if user:
        Users.del_exercise(user, eid)

    return jsonifym(user)

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

    data = {}

    errors = []

    data['name'] = request.form.get('name', 'Untitled')

    try:
        data['quantity'] = int(request.form.get('quantity', 0))
    except:
        errors.append('Quantity must be only digits 0-9')
    try:
        data['value'] = int(request.form.get('value', 0))
    except:
        errors.append('Value must be only digits 0-9')

    if not errors:
        user = Users.set_exercise(user, data, eid)
    else:
        print errors
        flash_list(errors, 'error')

    return jsonifym(user)

@app.route("/user/<user_id>/exercises", methods=['GET'])
def exercises(user_id):

    user = Users.find_by_id(user_id)

    if not user:
        return redirect('/')

    return render_template('app.html', user=user, app_context=jsonifym(user))

@app.route("/user/<user_id>/__details", methods=['GET'])
def details(user_id):

    user = Users.find_by_id(user_id)

    if not user:
        return redirect('/')

    return render_template('details.html', user=user, app_context=jsonifym(user))

@app.route("/user/__list", methods=['GET'])
def list():

    users = Users.find()

    if not users:
        return redirect('/')

    return render_template('list.html', users=users)


@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        email = request.form['email']

        if not email:
            return render_template('index.html')

        user = Users.find_one({'email': email})


        if not user:
            user_id = Users.create(email)
            sg = sendgrid.SendGridClient("justindonato750", app.config["SMTP_PASS"])
            message = sendgrid.Mail()
            message.add_to(email)
            message.set_subject("Welcome to Exercredit")
            message.set_html(render_template('welcome-inlined.html', user_id=user_id))
            message.set_from('welcome@exercredit.com')
            status, msg = sg.send(message)
            print status, msg

            return redirect('/user/%s/exercises?add=1' % user_id)
        else:
            print "flashing message"
            flash('Sorry, this email has already been registered. You should already be getting a daily email.', 'error')

    return render_template('index.html')

@app.route("/user/<user_id>/email", methods=['GET'])
def render_daily_mail(user_id):

    user = Users.find_by_id(user_id)
    if not user:
        return redirect('/')

    return render_template('html_mail.html', user=user)

@app.route("/welcome/<user_id>", methods=['GET'])
def render_welcome_mail(user_id):
    return render_template('welcome.html', user_id=user_id)

if __name__ == "__main__":
    app.run()
