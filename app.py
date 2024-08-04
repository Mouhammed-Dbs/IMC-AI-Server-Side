from flask import Flask, jsonify, request
from helpers import generateResponse,predictDisorderForUserAnswers,getStageLimits
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

@app.route('/generateQues/<string:typeQues>/<int:idQues>', methods=['POST'])
def generateQues(typeQues, idQues):
    if isAuth(request):
        limits = getStageLimits()
        idDisorder = request.args.get('idDisorder')
        if (((idDisorder == None ) and (0 < idQues <= limits["firstStageLimit"]) == False)) or (idDisorder != None and (0 < idQues <= limits["firstStageLimit"]+limits["secondStageLimit"][idDisorder]+limits["thirdStageLimit"][idDisorder]) == False):
            return jsonify({'error': True, 'message': 'Ques not found'})
        if idDisorder == None:
            idDisorder = '1'
        userRes = request.json.get('userRes', None)
        response_data = generateResponse(idQues, userRes, typeQues, idDisorder)
        response_data['limits'] = limits;
        return jsonify({
            'error': False,
            'message': 'This is the next question for you',
            'data': response_data,
        })
    return jsonify({'error': True, 'message': 'Invalid API key'}), 401

@app.route('/predictDisorderForFirstStage', methods=['POST'])
def predictDisorderForFirstStage():
    if isAuth(request):
        userAns = request.json.get('userAns', None)
        result = predictDisorderForUserAnswers(userAns);
        return jsonify({
                'error': False,
                'message': 'Prediction successfully',
                'data': {"disorderLabel":int(result)},
            })
    return jsonify({'error': True, 'message': 'Invalid API key'}), 401


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': True, 'message': 'Route not found'}), 404

if __name__ == '__main__':
    app.run(port=9000)
