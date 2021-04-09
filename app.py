from flask import Flask, render_template,request,flash,redirect,url_for,session,logging,jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import confg
from functools import wraps
from flask_pymongo import pymongo
from datetime import datetime
from bson import ObjectId
import logging
import sys
import dns
import os


app = Flask(__name__)
client = pymongo.MongoClient(confg.CONNECTION_STRING)
db = client.get_database(confg.DATABASE_NAME)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.secret_key = 'JaNcRfUjXn2r5u8x/A?D(G+KbPeSgVkYp3s6v9y$B&E)H@McQfTjWmZq4t7w!z%C'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    result = db.articles.count()
    all_articles = list(db.articles.find())
    if result > 0:
        return render_template('articles.html',len=len(all_articles),all_articles=all_articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html',len=0,msg=msg)


@app.route('/article/<string:id>/')
def article(id):
    single_article = list(db.articles.find({"_id":ObjectId(id)}))

    return render_template('article.html',single_article=single_article)


class RegisterForm(Form):
     name = StringField('Name', [validators.Length(min=1,max=50)])
     username = StringField('Username', [validators.Length(min=4,max=25)])
     email = StringField('Email',[validators.Length(min=6,max=50)])
     password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match!')
     ])
     confirm = PasswordField('Confirm Password')



@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        result = db.users.count({"username" : username})

        if result > 0:
            flash('Username taken! Try a different one.','danger')
            return redirect(url_for('register'))
        else:
            db.users.insert_one({"name": name, "email": email, "username" : username,"password" : password})
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))

    return render_template('register.html',form=form)


@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_submitted = request.form['password']

        result = db.users.count({'username' : username})

        if result > 0:
            data = list(db.users.find({'username' : username}))
            password = data[0]['password']

            if sha256_crypt.verify(password_submitted,password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    result = db.articles.find().count()
    allx_articles = list(db.articles.find({"author" : session['username']}))

    if result > 0:
        return render_template('dashboard.html',len=len(allx_articles),allx_articles=allx_articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html',len=0,msg=msg)


class ArticleForm(Form):
     title = StringField('Title', [validators.Length(min=1,max=200)])
     body = TextAreaField('Body', [validators.Length(min=30)])


@app.route('/add_article', methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method=='POST' and form.validate():
        title = form.title.data
        body = form.body.data

        now = datetime.now()

        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        db.articles.insert_one({"title": title, "body": body, "author" : session['username'],"create_date" : dt_string})

        flash('Article added!','success')
        return redirect(url_for('dashboard'))

    return render_template("add_article.html",form=form)


@app.route('/edit_article/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    single_article = list(db.articles.find({"_id" : ObjectId(id)}))

    form = ArticleForm(request.form)

    form.title.data = single_article[0]['title']
    form.body.data = single_article[0]['body']

    if request.method=='POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        app.logger.info(title)

        db.articles.update_one({'_id': ObjectId(id)}, {"$set": {'title': title,'body': body}})

        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template("edit_article.html",form=form)


@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):

    db.articles.delete_one({'_id': ObjectId(id)})

    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=False)
