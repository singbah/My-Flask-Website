from flask import Flask, redirect, render_template, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = b'2a34a567@#$%'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    photo = db.Column(db.String(120), nullable=False)

@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        return render_template('base.html', username=username)
    return render_template('base.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        photo = request.files.get('photo')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename )
            photo.save(photo_path)
        else:
            filename = None
        new_user = User(username=username, password=generate_password_hash(password), phone=phone, photo=filename)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            flash("Login successful")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    else:
        if 'username' in session:
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    if 'username' in session:
        username = session['username']
        session.pop('username', None)
        flash(f'You have been logged out, {username}')
        return redirect(url_for('index'))
    return redirect(url_for('logout'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)