import serial
from flask import Flask, render_template
from flask_socketio import SocketIO
from time import sleep
from Services.serial_service import SerialService
from threading import Thread, Event, Condition, current_thread
import time
from gevent import monkey
from queue import Queue
monkey.patch_all()
FILE_ARRAY = []
ARRAY_INDEX = 0 
RECORD = False
CONDITION = Condition()
DATAQUEUE = Queue()
APP = Flask(__name__)
SOCKETIO = SocketIO(APP)
THREAD = Thread()
SERIAL = serial.Serial(port = "/dev/ttyACM0", baudrate = 115200, timeout=0)

class CountThread(Thread):
    """Stream data on thread"""
    def __init__(self):
        #self.delay = 1
        super(CountThread, self).__init__()
        self._stop = Event()

    def get_data(self):
        """
        Get data and emit to socket
        """
        global FILE_ARRAY
        global RECORD
        global CONDITION
        while True:
            if not RECORD:
                with CONDITION:
                    CONDITION.notifyAll()
                    return
            else:
                val = SERIAL.readline()
                with CONDITION:
                    FILE_ARRAY.append(val)
                    if(len(FILE_ARRAY) % 128 == 0):
                        CONDITION.notifyAll()
    def run(self):
        """Default run method"""
        self.get_data()

    def stop(self):
        """Stop thread"""
        print("Stopping thread...")
        self._stop.set()
 
    def stopped(self):
        return self._stop.isSet()


@APP.route('/')
def index():
    """Index route"""
    return render_template("test.html")

@SOCKETIO.on('connect', namespace='/flask-socketio-demo')
def connect_socket():
    """Handle socket connection"""
    print("Client connected")


@SOCKETIO.on('disconnect', namespace='/flask-socketio-demo')
def disconnect_socket():
    """Handle socket disconnection"""
    print("Client disconnected")
    global RECORD
    global THREAD
    RECORD = False
    THREAD.join()
    print("Recording stopped")
    print("Thread status: ", THREAD.isAlive())

#Receive "startRecording" event from client
@SOCKETIO.on('startRecording', namespace='/flask-socketio-demo')
def startRecord(incoming):
    """Start recording"""
    print(incoming)
    global RECORD
    global THREAD
    RECORD = True
    # Start thread
    print("Recording started")
    print("Thread status: ", THREAD.isAlive())
    #if not THREAD.isAlive():
    THREAD = CountThread()
    THREAD.start()

@SOCKETIO.on('getData', namespace='/flask-socketio-demo')
def getData(incoming):
    """Get data from queue"""
    print("Getting data from queue")
    tempArray = []
    global DATAQUEUE
    global ARRAY_INDEX
    global FILE_ARRAY
    global CONDITION
    with CONDITION:
        print("aaaaa")
        while len(FILE_ARRAY) == 0:
            print("Waiting for data...1")
            CONDITION.wait()
        while (ARRAY_INDEX <= len(FILE_ARRAY)-128):
            if len(FILE_ARRAY) % 128 == 0:
                print("Processing...")
                tempArray = [x for x in [x.decode().strip().split(".")[0][0:3] for x in FILE_ARRAY if len(x.decode().strip().split(".")[0][0:3]) > 2][128*ARRAY_INDEX:128*(1+ARRAY_INDEX)]]
            if len(tempArray) < 128:
                CONDITION.wait()
            else:
                print("Temp array: ", tempArray)
                SOCKETIO.emit("sendData", {"test":tempArray}, namespace='/flask-socketio-demo')
                ARRAY_INDEX += 1
                print("Data sent")

#Receive "stopRecording" event from client
@SOCKETIO.on('stopRecording', namespace='/flask-socketio-demo')
def stopRecording(incoming):
    """Stop recording"""
    print("Stopping recording...")
    global FILE_ARRAY
    global ARRAY_INDEX 
    ARRAY_INDEX = 0
    #print([x.decode().strip() for x in FILE_ARRAY])
    #Save list to a file:
    with open("test.txt", "w") as f:
            f.write(', '.join([x.decode().strip() for x in FILE_ARRAY]))

    print(incoming)
    global RECORD
    global THREAD
    RECORD = False
    THREAD.join()
    print("Recording stopped")



if __name__ == '__main__':
    print("Connecting...")
    SOCKETIO.run(APP, host='192.168.1.250')

    