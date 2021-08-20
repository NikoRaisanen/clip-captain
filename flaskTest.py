import os
import time
import backendService
from backendService import Clip, VideoObj
from flask import Flask, flash, request, redirect, url_for, render_template, session, json
from werkzeug.utils import secure_filename

global globalStatus
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
    global globalStatus
    globalStatus = "Press the upload button to get started!"
    session['gameName'] = request.form['gameName']
    session['videoTitle'] = request.form['videoTitle']
    session['privacyStatus'] = request.form['privacyStatus']
    session['tags'] = request.form['tags']
    session['description'] = request.form['description']
    session['status'] = 'status set in get_data()'
    # return redirect(url_for('home'))
    file = request.files['thumbnail']
    filename = secure_filename(file.filename)
    session['thumbnailName'] = filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(f"Here is the {filename}")

    

    
    return render_template('process.html', gameName=session['gameName'], videoTitle=session['videoTitle'], thumbnail=filename, privacyStatus=session['privacyStatus'], tags=session['tags'], description=session['description'])

# Delete this route and put processing.html into the render_template above
@app.route('/execute_program')
def execute_program():

    global globalStatus
    globalStatus = "Starting Execute_program"
    Clip.gameName = session['gameName']
    thumbnail = os.path.join(os.getcwd(), 'thumbnails', session['thumbnailName'])
    filename = Clip.gameName + '.mp4'
    videoStruct = VideoObj(session['gameName'], filename, session['videoTitle'], thumbnail, session['tags'], session['description'], session['privacyStatus'])
    transition = 'assets/tvstatictransition.mp4'
    globalStatus = "Authenticating..."

    ytService = backendService.get_authenticated_service()
    credentials = backendService.get_credentials()
    globalStatus = 'Getting clip information...'
    gameId = backendService.get_game_id(session['gameName'], credentials)
    clips = backendService.get_clip_info(credentials, gameId, numClips=2)
    globalStatus = 'Downloading clips...'
    backendService.download_clips(clips, videoStruct)
    globalStatus = 'Combining clips...'
    vidPath = backendService.combine_clips(clips, transition)
    videoStruct.filename = vidPath
    # ytService = get_authenticated_service()
    globalStatus = 'Beginning video upload!'
    backendService.upload_video(ytService, videoStruct)
    globalStatus = "Woo hoo! The video is uploaded, check your channel to see the video!"
    return render_template('process.html', gameName=session['gameName'], videoTitle=session['videoTitle'], thumbnail=session['thumbnailName'], privacyStatus=session['privacyStatus'], tags=session['tags'], description=session['description'])

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
    message = {'status': globalStatus}
    return json.jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)
    