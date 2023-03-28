import serial
from flask import Flask, render_template
from flask_socketio import SocketIO
from time import sleep
import numpy as np
from scipy.io.wavfile import write
from functools import reduce
from Services.serial_service import SerialService
#from threading import Thread, Event, Condition, current_thread
import time
from multiprocessing import Process, Event, Condition, current_process, Manager, Value, Queue
from gevent import monkey
#from queue import Queue
monkey.patch_all()
FILE_ARRAY = []
FILE_QUEUE = Queue()
SAMPLE_RATE = 1500
ARRAY_INDEX = 0 
RECORD = Value('b', False)
SEND = False
CONDITION = Condition()
APP = Flask(__name__)
SOCKETIO = SocketIO(APP)
# THREAD = Thread()
PROCESS = Process()
SERIAL = serial.Serial(port = "/dev/ttyACM0", baudrate = 115200, timeout=0)

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
        global RECORD
        while True:
            print("Current ProcessID: ", current_process().pid)
            print("Record status: ", self.record.value)
            if not self.record.value:
                print("Stopping recording1")
                return
            else:
                print("Recording....")
                val = SERIAL.readline()
                self.queue.put(val)
                sleep(0.0001)


    def run(self):
        """Default run method"""
        self.get_data()


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
    global PROCESS
    RECORD.value = False
    PROCESS.join()
    print("Recording stopped")
    #print("Thread status: ", THREAD.isAlive())

#Receive "startRecording" event from client
@SOCKETIO.on('startRecording', namespace='/flask-socketio-demo')
def startRecord(incoming):
    """Start recording"""
    print(incoming)
    global RECORD
    global PROCESS
    RECORD.value = True
    # Start thread
    print("Recording started")
    #print("Thread status: ", THREAD.isAlive())
    #if not THREAD.isAlive():
    PROCESS = GetSerial(FILE_QUEUE, RECORD)
    PROCESS.start()

@SOCKETIO.on('getData', namespace='/flask-socketio-demo')
def getData(incoming):
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
        if len(tempArray) == 128:
            SOCKETIO.emit("sendData", {"test":tempArray}, namespace='/flask-socketio-demo')
            print("Data sent: ", tempArray)
            tempArray = []
        timeoutStart = time.time()
        while FILE_QUEUE.empty() and SEND:
            sleep(0.01)
            timeoutEnd = time.time()
            print("Waiting for data...2", timeoutEnd)
            if timeoutEnd - timeoutStart > 5:
                return 
            


    # print("aaaaa")
    # while len(FILE_ARRAY) == 0:
    #     print("Waiting for data...1")
    # while (SEND):
    #     sleep(0.01)
    #     #print("Checking length of array...")
    #     print("Length of array: ", len(FILE_ARRAY))
    #     if len(FILE_ARRAY) > 128:
    #         print("Processing...")
    #         tempArray = [x for x in [x.decode().strip().split(".")[0][0:3] for x in FILE_ARRAY if len(x.decode().strip().split(".")[0][0:3]) > 2][128*ARRAY_INDEX:128*(1+ARRAY_INDEX)]]
    #     if len(tempArray) >= 128:
    #         SOCKETIO.emit("sendData", {"test":tempArray}, namespace='/flask-socketio-demo')
    #         ARRAY_INDEX += 1
    #         print("Data sent: ", ARRAY_INDEX)
    #     else:
    #         while(ARRAY_INDEX*128 <= len(FILE_ARRAY)-128):
    #             print("Waiting for data...2")
    #             sleep(0.1)
        

#Receive "stopRecording" event from client
@SOCKETIO.on('stopRecording', namespace='/flask-socketio-demo')
def stopRecording(incoming):
    """Stop recording"""
    print("Stopping recording...")
    global FILE_ARRAY
    global ARRAY_INDEX 
    global SEND
    ARRAY_INDEX = 0
    SEND = False
    print(incoming)
    global RECORD
    global PROCESS
    RECORD.value = False
    print("PID of child process: ", PROCESS.pid)
    
    PROCESS.join()
    print("Recording stopped")

    #Save list to a file:
    print("Encoding file...")
    # saveWav = np.array([x for x in [x.decode().strip().split(".")[0][0:3] for x in FILE_ARRAY if len(x.decode().strip().split(".")[0][0:3]) > 2]])
    # meanVal = reduce(lambda a, b: a + b, saveWav)/len(saveWav)
    # transformedSamples = [x - meanVal for x in saveWav]
    # waveform_scaled = np.int16(
    # transformedSamples/np.max(np.abs(transformedSamples)) * 32767)
    # print("Writing file...")
    # write('test.wav', SAMPLE_RATE, waveform_scaled)
    with open("test.txt", "w") as f:
        f.write(", ".join(FILE_ARRAY))


    



if __name__ == '__main__':
    print("Connecting...")
    SOCKETIO.run(APP, host='192.168.1.250')

    