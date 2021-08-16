import os
import backendService
from flask import Flask, flash, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'any random string'

# Declaring required global variables


# If GET request, serve index.html
@app.route('/')
def home():
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
    return "handle_data() completed"

@app.route('/test')
def script1():
    credentials = backendService.get_credentials()
    game_id = backendService.get_game_id('Dota 2', credentials)
    return f"<h1>The game ID for Dota 2 is {game_id}</h1>"

@app.route('/var')
def var_test():
    varOutput = f"{session['gameName']}\n{session['videoTitle']}\n{session['thumbnail']}\n{session['privacyStatus']}\n{session['tags']}\n{session['description']}"
    return varOutput
if __name__ == '__main__':
    app.run(debug=True)
    