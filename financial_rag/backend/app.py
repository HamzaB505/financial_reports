from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64
from api.query_handler import QueryHandler
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["FLASK_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Dummy data for demonstration purposes
financial_data = {
    'stocks': [100, 120, 80, 130, 150],
    'bonds': [50, 60, 55, 65, 70],
    'crypto': [200, 180, 220, 210, 230]
}

@app.route('/')
def landing_page():
    return render_template('home.html')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# push context manually to app
with app.app_context():
    db.create_all()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for('signup'))

        new_user = User(email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash('Thank you for signing up!')
        return redirect(url_for('chatbot'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('chatbot'))
        else:
            flash('Invalid credentials.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form['message']
        
        # Prepare the prompt
        print(user_input)
        handler = QueryHandler()
        print("handler loaded")
        try:
            response = handler.rag_query(query=user_input)
        except Exception:
            response = "Error handler, check code or input"
            print(response)
        return jsonify({'response': response})

    
    return render_template('chatbot.html')


@app.route('/dashboard')
def dashboard():
    # Create a plot and display it
    fig, ax = plt.subplots()
    ax.plot(financial_data['stocks'], label='Stocks')
    ax.plot(financial_data['bonds'], label='Bonds')
    ax.plot(financial_data['crypto'], label='Crypto')
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('dashboard.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
