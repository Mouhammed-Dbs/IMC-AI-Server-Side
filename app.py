from flask import Flask, jsonify, request
from helpers import generateResponse
import os
import gdown

def download_file_from_google_drive(file_id, destination):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, destination, quiet=False)

files = ['data/vectors0.json','data/vectors1.json','data/vectors2.json']
id_files = ['1mrMjVBJh6f46uUVqVx4SKbMeVbMWqhh_','1SiXGYqx2UUa1FmCeFT_edxc_n5eHdKzh','1Kv_rBMpLexnzwPHEc5nFa_xyGtJHKzDy']

for i,file_path in enumerate(files):
    if os.path.exists(file_path)==False:
        download_file_from_google_drive(id_files[i],"data/vectors"+str(i)+".json")

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
        if 0 < idQues <= 10:
            userRes = request.json.get('userRes', None)
            return jsonify({
                'error': False,
                'message': 'This is the next question for you',
                'data': generateResponse(idQues,userRes, typeQues),
            })
        else:
            return jsonify({'error': True, 'message': 'Ques not found'}), 404
    return jsonify({'error': True, 'message': 'Invalid API key'}), 401



@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error':True,'message': 'Route not found'}), 404

if __name__ == '__main__':
    app.run(port=9000)
