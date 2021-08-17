import os
import time
import backendService
from flask import Flask, flash, request, redirect, url_for, render_template, session, json
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'any random string'

# Declaring required global variables

# def script_output():
#     output = execute('./script')
#     return render_template('template_name.html',output=output)

# If GET request, serve index.html
@app.route('/')
def home():
    session['status'] = 'status set in home()'
    return render_template('index.html')

@app.route('/handle_data', methods=['POST'])
def handle_data():
    # ytService = backendService.get_authenticated_service()

    session['gameName'] = request.form['gameName']
    session['videoTitle'] = request.form['videoTitle']
    session['thumbnail'] = request.form['thumbnail']
    session['privacyStatus'] = request.form['privacyStatus']
    session['tags'] = request.form['tags']
    session['description'] = request.form['description']
    return redirect(url_for('home'))

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
    