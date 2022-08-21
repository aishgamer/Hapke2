"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request
import os, shutil
from werkzeug.utils import secure_filename
from hapke2 import app
from .cerebrum import launcher as dfr

# create the folders when setting up your app
os.makedirs(os.path.join(app.instance_path, 'user_files'), exist_ok=True)
os.makedirs(os.path.join(app.instance_path, 'ref_files'), exist_ok=True)

# Delete user files if any
folder = os.path.join(app.instance_path, 'user_files')
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/input_session',methods=['GET'])
def session_input():
    img_data = dfr.hello()
    return img_data

@app.route('/input_upload',methods=[ "GET",'POST'])
def input_upload_file():
    isthisFile=request.files.get('file')
    filename = 'input_file.txt'
    isthisFile.save(os.path.join(app.instance_path, 'user_files', secure_filename(filename)))
    web_response = dfr.read_input()
    return web_response
    
@app.route('/input_preprocess',methods=['GET','POST'])
def input_preprocess():
    fdata = request.form
    web_response = dfr.preprocess(fdata)
    return web_response