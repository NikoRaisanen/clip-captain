import os
import time
import backendService
from flask import Flask, flash, request, redirect, url_for, render_template, session, json
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Max thumbnail upload size of 2MB
app.config['MAX_CONTENT-PATH'] = 2 * 1024 * 1024
app.secret_key = 'any random string'


# If GET request, serve index.html
@app.route('/')
def home():
    session['status'] = 'status set in home()'
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    # ytService = backendService.get_authenticated_service()

    session['gameName'] = request.form['gameName']
    session['videoTitle'] = request.form['videoTitle']
    session['privacyStatus'] = request.form['privacyStatus']
    session['tags'] = request.form['tags']
    session['description'] = request.form['description']
    session['status'] = 'status set in get_data()'
    print(session['thumbnail'])
    # return redirect(url_for('home'))
    file = request.files['thumbnail']

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(f"Here is the {filename}")
    return render_template('process.html', gameName=session['gameName'], videoTitle=session['videoTitle'], thumbnail=filename, privacyStatus=session['privacyStatus'], tags=session['tags'], description=session['description'], status=session['status'])

# Delete this route and put processing.html into the render_template above
@app.route('/process')
def process_video():
    return render_template('process.html')

@app.route('/test')
def script1():
    print("beginning execution of script1()")
    print("setting status to 'mystatus'")
    session['status'] = 'mystatus'
    credentials = backendService.get_credentials()
    print("got credentials")
    game_id = backendService.get_game_id('Dota 2', credentials)
    x = f"<h1>The game ID for Dota 2 is {game_id}</h1>"
    return render_template('index.html', x=x)

@app.route('/var')
def var_test():
    # backendService.all_in_one()
    return render_template('index.html')

@app.route('/status')
def status():
    message = {'status': session['status']}
    return json.jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)
    