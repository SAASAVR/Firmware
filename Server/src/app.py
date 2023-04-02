import serial
from flask import Flask, render_template
#from flask_socketio import SocketIO
from time import sleep
import numpy as np
import socketio
from scipy.io.wavfile import write
from functools import reduce
from Services.serial_service import SerialService
#from threading import Thread, Event, Condition, current_thread
import time
from multiprocessing import Process, Event, Condition, current_process, Manager, Value, Queue
from gevent import monkey
import io
import librosa
import librosa.display
import pymongo
from PIL import Image
import base64
#from queue import Queue
#monkey.patch_all()

with open('mongodbKey', 'r') as file:
    MONGO_URL = file.read()
dbClient = pymongo.MongoClient(MONGO_URL)
DATABASE_NAME = "mydatabase"
COLLECTION_NAME = "AudiosTest"

FILE_ARRAY = []
FILE_QUEUE = Queue()
SAMPLE_RATE = 1500
ARRAY_INDEX = 0 
RECORD = Value('b', False)
SEND = False
CONDITION = Condition()
#APP = Flask(__name__)
#SOCKETIOSERVER = SocketIO(APP)
SOCKETIO = socketio.Client()
# THREAD = Thread()
PROCESS = Process()
SERIAL = serial.Serial(port = "/dev/ttyACM0", baudrate = 921600, timeout=0)

class GetSerial(Process):
    """Stream data on thread"""
    def __init__(self, queue, record):
        #self.delay = 1
        super(GetSerial, self).__init__()
        self.queue = queue
        self.record = record


    def get_data(self):
        """
        Get data and emit to socket
        """
        print("Recording....")
        while True:
            if not self.record.value:
                print("Stopping recording1")
                return
            else:
                val = SERIAL.readline()
                self.queue.put(val)
                sleep(0.00001)

    def run(self):
        """Default run method"""
        self.get_data()


# @APP.route('/')
# def index():
#     """Index route"""
#     return render_template("test.html")

# @SOCKETIO.on('connect')
# def connect_socket(self):
#     """Handle socket connection"""
#     print("Client connected: ")

@SOCKETIO.on('disconnect')
def disconnect_socket():
    """Handle socket disconnection"""
    print("Client disconnected")
    global RECORD
    global PROCESS
    RECORD.value = False
    if(PROCESS.is_alive()):
        PROCESS.join()
    print("Recording stopped")
    #print("Thread status: ", THREAD.isAlive())


#Receive "startRecording" event from client
@SOCKETIO.on('UI-record-request')
def startRecord(incoming):
    global SAMPLE_RATE
    """Start recording"""
    print(incoming)
    SOCKETIO.emit("SAAS-recording", {"samplerate":SAMPLE_RATE})
    global RECORD
    global PROCESS
    RECORD.value = True
    # Start thread
    print("Recording started")
    #print("Thread status: ", THREAD.isAlive())
    #if not THREAD.isAlive():
    PROCESS = GetSerial(FILE_QUEUE, RECORD)
    PROCESS.start()

@SOCKETIO.on("UI-ready-for-data")
def getData():
    """Get data from queue"""
    print("Getting data from queue")
    tempArray = []
    global ARRAY_INDEX
    global FILE_QUEUE
    global FILE_ARRAY
    global SEND
    SEND = True

    while SEND or not FILE_QUEUE.empty():
        
        val = FILE_QUEUE.get().decode().strip().split(".")[0][0:3]
        if len(val) == 3:
            tempArray.append(val)
            FILE_ARRAY.append(val)
        else:
            print("Invalid data: ", val)
        if len(tempArray) == 128:
            SOCKETIO.emit("SAAS-send-data", {"vals":tempArray})
            #print("Data sent: ", tempArray)
            tempArray = []
        timeoutStart = time.time()
        while FILE_QUEUE.empty() and SEND:
            sleep(0.01)
            timeoutEnd = time.time()
            #print("Waiting for data...2", timeoutEnd)
            if timeoutEnd - timeoutStart > 5:
                break 
            
#Receive "stopRecording" event from client
@SOCKETIO.on('UI-stop-request')
def stopRecording():
    """Stop recording"""
    print("Stopping recording...")
    global FILE_ARRAY
    global ARRAY_INDEX 
    global SEND
    ARRAY_INDEX = 0
    SEND = False
    global RECORD
    global PROCESS
    RECORD.value = False
    print("PID of child process: ", PROCESS.pid)

    if(PROCESS.is_alive()):
        PROCESS.join()
    print("Recording stopped")
    SOCKETIO.emit("SAAS-stopping-recording",)

    #Save list to a file:
    print("Encoding file...")
    with open("test.txt", "w") as f:
        f.write(", ".join(FILE_ARRAY))
    saveFile([int(x) for x in FILE_ARRAY], SAMPLE_RATE)
    print("File saved")
    


@SOCKETIO.on("UI-connect")
def UIConnected(data):
    """event listener for when the UI connects"""
    print("UI has connected")
    SOCKETIO.emit("SAAS-connect")
    time.sleep(1)
    print("Sending ready...")
    print(data)
    SOCKETIO.emit("SAAS-ready")
    

def saveFile(audioWaveform,sps):
    meanVal = sum(audioWaveform)/len(audioWaveform)
    transformedSamples = [x - meanVal for x in audioWaveform]

    npArray = np.array(audioWaveform)

    print("Max value in npArraY: " + str(npArray.max()))
    # Removing outliers greater than 300 and less than 200 from npArray
    npArray = npArray[npArray < 600]
    npArray = npArray[npArray > 200]
    print(len(npArray))
    # Scale waveform to 16-bit range
    waveform_scaled = np.int16(
        transformedSamples/np.max(np.abs(transformedSamples)) * 32767)

    # Play the waveform out the speakers
    print("Saving WAV file...")
    write('test.wav', sps, waveform_scaled)




if __name__ == '__main__':
    print("Connecting...")
    SOCKETIO.connect('http://192.168.1.93:5000')
    print("Connected...")
    SOCKETIO.emit("SAAS-connect")
    time.sleep(1)
    print("Sending ready...")
    SOCKETIO.emit("SAAS-ready")
    #SOCKETIO.run(APP, host='192.168.1.250')

    