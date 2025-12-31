import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
# import Gesture_Controller_Gloved as Gesture_Controller
import app
from threading import Thread


# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status
gesture_active = False   # <<< FIX >>> track gesture state


# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")
    reply("I am Proton, how may I help you?")


# Set Microphone parameters
with sr.Microphone() as source:
    r.energy_threshold = 500
    r.dynamic_energy_threshold = False


# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        r.non_speaking_duration = 0.5   # tolerate pauses
        voice_data = ''

        try:
            audio = r.listen(
                source,
                timeout=5,               # time to START speaking
                phrase_time_limit=5      # total speech duration
            )
            voice_data = r.recognize_google(audio)

        except sr.WaitTimeoutError:
            # No speech detected — NOT an error
            return ""

        except sr.UnknownValueError:
            print('cant recognize')
            return ""

        except sr.RequestError:
            reply('Sorry my Service is down. Please check your Internet connection')
            return ""

        except OSError as e:
            # <<< THIS IS THE IMPORTANT FIX >>>
            # Handles: [Errno -9988] Stream closed
            print("AUDIO STREAM ERROR:", e)
            time.sleep(0.5)   # allow mic to recover
            return ""

        return voice_data.lower()


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path, gesture_active

    print("HEARD:", voice_data)     # <<< FIX >>> debug speech input

    # <<< FIX >>> properly remove wake word
    voice_data = voice_data.replace('proton', '').strip()

    app.eel.addUserMsg(voice_data)

    if is_awake is False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Proton!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif 'search' in voice_data:
        reply('Searching for ' + voice_data.split('search')[1])
        url = 'https://google.com/search?q=' + voice_data.split('search')[1]
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif 'location' in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()

    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.daemon = True        # <<< FIX >>> allow clean exit
            t.start()
            gesture_active = True
            reply('Launched Successfully')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            gesture_active = False
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')

    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')

    elif 'page' in voice_data or 'pest' in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')

    # File Navigation
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status is True:
        counter = 0
        if 'open' in voice_data:
            try:
                idx = int(voice_data.split(' ')[-1]) - 1
                if isfile(join(path, files[idx])):
                    os.startfile(path + files[idx])
                    file_exp_status = False
                else:
                    path = path + files[idx] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
            except:
                reply('You do not have permission to access this folder')

        elif 'back' in voice_data:
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a) + '//'
                files = listdir(path)
                filestr = ""
                for f in files:
                    counter += 1
                    filestr += str(counter) + ':  ' + f + '<br>'
                reply('ok')
                app.ChatBot.addAppMsg(filestr)

    else:
        reply('I am not functioned to do this !')


# ------------------Driver Code--------------------

t1 = Thread(target=app.ChatBot.start)
t1.daemon = True
t1.start()

# Wait until ChatBot is ready
while not app.ChatBot.started:
    time.sleep(0.5)

wish()

voice_data = None

while True:
    try:
        if app.ChatBot.isUserInput():
            voice_data = app.ChatBot.popUserInput().lower()
        else:
            # <<< FIX >>> do not block mic when gesture is active
            if not gesture_active:
                voice_data = record_audio()
            else:
                time.sleep(0.1)
                continue

        if voice_data:
            respond(voice_data)

    except SystemExit:
        reply("Exit Successful")
        break
    except Exception as e:
        print("EXCEPTION:", e)
        break
