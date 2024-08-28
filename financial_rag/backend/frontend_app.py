from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import io
import base64
from api.query_handler import QueryHandler
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
# Dummy data for demonstration purposes
financial_data = {
    'stocks': [100, 120, 80, 130, 150],
    'bonds': [50, 60, 55, 65, 70],
    'crypto': [200, 180, 220, 210, 230]
}

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Handle the signup or login logic here
        return redirect(url_for('chatbot'))
    return render_template('signup.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # Prepare the prompt
        print(user_input)
        handler = QueryHandler()
        print("handler loaded")
        try:
            response = handler.rag_query(query=user_input)
        except Exception:
            response = "Error handler, check code or input"
            print(response)
        
        return render_template('index.html',
                               user_input=user_input,
                               response=response)
    
    return render_template('index.html')


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
