from flask import Flask, render_template, request
from api.query_handler import QueryHandler
from dotenv import load_dotenv
import chromadb
import asyncio
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
            print('Error handler, check code or input')
            response = "Error"
        
        
        return render_template('index.html',
                               user_input=user_input,
                               response=response)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
