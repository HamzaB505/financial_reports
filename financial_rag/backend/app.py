from flask import Flask, render_template, request
from api.query_handler import QueryHandler
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()



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

if __name__ == '__main__':
    app.run(debug=True)
