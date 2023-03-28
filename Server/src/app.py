import serial
from flask import Flask, render_template
from flask_socketio import SocketIO
from time import sleep
from Services.serial_service import SerialService
from threading import Thread, Event, Condition
import time
from gevent import monkey
from queue import Queue
monkey.patch_all()

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
        outputSamples = []
        counter = 0
        while counter < 1024:
            val = SERIAL.readline().strip()
            print(val)
            if val is not b'':
                #print(val)
                try:
                    parsedVal = float(val.decode().strip())
                    if(parsedVal > 0):
                        #print(float(val.decode()))
                        #print(float(val))
                        if(parsedVal > 0):
                            if(parsedVal > 700) or (parsedVal < 100):
                                print("Corrected from...", parsedVal)
                                if(counter != 0):
                                    parsedVal = outputSamples[counter-1]
                                else:
                                    parsedVal = 240
                        #print(float(val))
                            outputSamples.append(float(parsedVal))
                            counter += 1

                # serialThread.start()
                except:
                    parsedVal = float(val.decode().strip().split(".")[0])
                    if(parsedVal > 0):
                        if(parsedVal > 700) or (parsedVal < 100):
                            print("Corrected from...", parsedVal)
                            if(counter != 0):
                                parsedVal = outputSamples[counter-1]
                            else:
                                parsedVal = 240
                        
                    #print(float(val))
                        outputSamples.append(float(parsedVal))
                        counter += 1
        with CONDITION:
            DATAQUEUE.put(outputSamples.copy())
            CONDITION.notifyAll()
        # outputSamples.clear()
        # print("Added to queue...")
        # print("Queue size: ", DATAQUEUE.qsize())


        

 
            
    def run(self):
        """Default run method"""
        global RECORD
        while True:
            if not RECORD:
                with CONDITION:
                    print("Recording stopped IN THREAD")
                    CONDITION.notifyAll()
                    return
            else:
                print("Recording started IN THREAD")
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
    global DATAQUEUE
    global CONDITION
    with CONDITION:
        print("aaaaa")
        while DATAQUEUE.qsize() == 0:
            print("Waiting for data...1")
            CONDITION.wait()
        while DATAQUEUE.qsize() > 0:
            print("Sending data...")
            SOCKETIO.emit("sendData", {"test":DATAQUEUE.get()}, namespace='/flask-socketio-demo')
            print("Data sent")
            if DATAQUEUE.qsize() == 0:
                print("Waiting for data...2")
                CONDITION.wait()

#Receive "stopRecording" event from client
@SOCKETIO.on('stopRecording', namespace='/flask-socketio-demo')
def stopRecording(incoming):
    print(incoming)
    global RECORD
    global THREAD
    RECORD = False
    THREAD.join()
    print("Recording stopped")
    print("Thread status: ", THREAD.isAlive())


if __name__ == '__main__':
    print("Connecting...")
    SOCKETIO.run(APP, host='192.168.1.250')

    