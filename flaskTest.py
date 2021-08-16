import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# If GET request, serve index.html
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/handle_data', methods=['POST'])
def handle_data():
    gameName = request.form['gameName']
    videoTitle = request.form['videoTitle']
    thumbnail = request.form['thumbnail']
    privacyStatus = request.form['privacyStatus']
    tags = request.form['tags']
    description = request.form['description']
    info = videoTitle + thumbnail + privacyStatus + tags + description
    print(info)
    return info
if __name__ == '__main__':
    app.run(debug=True)