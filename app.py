from flask import Flask
from flask import render_template
from flask import request
from turbo_flask import Turbo
import threading
import asyncio
import time
import json
import sys
import os
from flask import url_for
from colorthief import ColorThief
from media import MediaPlayer
from winsdk.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager


# pyinstaller --onefile --add-data templates;templates --add-data static;static --icon="C:\Users\HP\Desktop\Python Scripts\mediacontrol\static\play.png"  app.py

template_folder = "templates"
static_folder = "static"
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

app = Flask(__name__)
turbo = Turbo()
turbo.init_app(app)
mp = MediaPlayer()
async def initialize():
    await mp.create()
def update_load():
    with app.app_context():
        while True:
            time.sleep(0.5)
            turbo.push(turbo.replace(render_template('media.html'), 'song'))


with app.app_context():
    threading.Thread(target=update_load).start()

@app.route("/", methods=['GET', 'POST'])
def home(current="No Song Playing"):
    if request.method == 'POST':
        if 'toggle' in request.form:
            print("playing")
            asyncio.run(mp.play_pause())
        elif 'back' in request.form:
            print("previous track")
            asyncio.run(mp.previous_track)
        elif 'next' in request.form:
            print("next track")
            asyncio.run(mp.next_track())
    return render_template("index.html", song=current)

@app.route('/send')
def send():
    return "<a href=%s>file</a>" % url_for('static', filename='colors.json')

@app.context_processor
def getsong():
    songinfo = asyncio.run(mp.get_media_info())
    mp.update_thumbnail()
    button_label = "play"
    if(songinfo['status'] == 5): #paused
        button_label = "play"
    elif(songinfo['status'] == 4): #playing
        button_label = "pause"

    return {'song': songinfo['title'], 'position': songinfo['artist'], "label": button_label}


app.run(debug=False, host="0.0.0.0")
