from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)
from scheduler import smart_schedule

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # keep this secret in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))  # For production, hash this!

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    duration = db.Column(db.Float)
    deadline = db.Column(db.String(20))  # kept as string for now
    priority = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    raw = [t.__dict__ for t in tasks]
    for r in raw:
        r.pop('_sa_instance_state', None)
    scheduled = smart_schedule(raw)
    return render_template('index.html', tasks=scheduled)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task = Task(
        title=request.form['title'],
        duration=float(request.form['duration']),
        deadline=request.form['deadline'],
        priority=int(request.form['priority']),
        user_id=current_user.id
    )
    db.session.add(task)
    db.session.commit()
    flash("Task added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    task = Task.query.get(id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted!", "danger")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']  # for production, verify hash
        ).first()
        if user:
            login_user(user)
            flash("Welcome back!", "info")
            return redirect(url_for('index'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash("User already exists", "warning")
            return redirect(url_for('register'))
        user = User(
            username=request.form['username'],
            password=request.form['password']  # for production, store hash
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.", "secondary")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
