from flask import Flask, jsonify, request
from helpers import generateQuesForSymptom,generateQuesForFirstStage
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return "Welcome to the IMC Server"

def isAuth(request):
    api_key = request.headers.get('Authorization')
    if api_key and api_key.startswith('Bearer '):
        api_key = api_key.split('Bearer ')[1]
        if api_key == os.getenv('SECRET_KEY'):
            return True
    return False

@app.route('/generateQuesForFirstStage/<string:typeQues>/<int:idQues>', methods=['GET'])
def update_item(idQues,typeQues):
    if isAuth(request):
        if 0 < idQues <= 10:
            return jsonify({'error':False,'message': 'This is next question for you','data':generateQuesForFirstStage(idQues,typeQues)})
        else:
            return jsonify({'error':True,'message': 'Ques not found'}), 404
    return jsonify({'error':True,'message': 'Invalid API key'}), 401


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error':True,'message': 'Route not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
