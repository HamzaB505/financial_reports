from flask import (Flask, render_template, request, redirect,
                   url_for, jsonify, session, flash)
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io
import base64
from api.query_handler import QueryHandler
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
from api.finance_modeling_api import Finance_API
import plotly.graph_objs as go
import json
from flask import jsonify

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["FLASK_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
        return redirect(url_for('news_details'))
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
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/get_plot_data', methods=['POST'])
def get_plot_data():
    company = request.json.get('company')
    plot_type = request.json.get('plot_type')

    financial_data = {
        'AAPL': {
            'revenue': [200, 220, 230, 240, 250],
            'profit': [50, 55, 60, 65, 70],
            'quarters': ['Q1', 'Q2', 'Q3', 'Q4', 'Q1']
        },
        'MSFT': {
            'revenue': [150, 160, 170, 180, 190],
            'profit': [40, 42, 45, 50, 55],
            'quarters': ['Q1', 'Q2', 'Q3', 'Q4', 'Q1']
        }
    }

    if company not in financial_data:
        return jsonify({'plot_html': '<div>Invalid company</div>'})

    if plot_type == 'revenue_vs_profit':
        plot_html = generate_revenue_vs_profit_plot(company, financial_data)
    else:
        plot_html = '<div>Invalid plot type</div>'

    return jsonify({'plot_html': plot_html})

def generate_revenue_vs_profit_plot(company, financial_data):
    data = financial_data[company]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data['quarters'],
        y=data['revenue'],
        name='Revenue',
        marker_color='indianred'
    ))

    fig.add_trace(go.Bar(
        x=data['quarters'],
        y=data['profit'],
        name='Profit',
        marker_color='lightsalmon'
    ))

    fig.update_layout(
        title=f'Revenue vs Profit for {company}',
        xaxis=dict(title='Quarter'),
        yaxis=dict(title='Amount (in millions)'),
        barmode='group'
    )

    plot_html = fig.to_html(full_html=False)
    return plot_html

@app.route('/news_details')
def news_detail():
    # Example article data (in a real app, fetch from a database)
    fapi = Finance_API()
    articles = fapi.get_news()["content"]
    article = articles[0]
    related_articles = articles[1:]
    return render_template('news_details.html', article=article, related_articles=related_articles)


if __name__ == '__main__':
    app.run(debug=True)
