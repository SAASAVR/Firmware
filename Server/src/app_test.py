from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from Testing.test_values import TestValues
from Services.serial_service import SerialService
from Services.processing_service import ProcessingService
import threading
import datetime

outputSamples = []
app = Flask(__name__)
socketio = SocketIO(app)

values = TestValues(20000).getVals()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect_socket():
        print('Client connected')
    
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)


def RunService():
    try:
        serialService = SerialService("/dev/ttyACM0", 115200, socketio)
    except:
         serialService = SerialService("/dev/ttyACM1", 115200, socketio)
    while 1:
        outputSamples = serialService.RetrieveData()
        socketio.emit('test', "TESTING DATA!")
    serialService.ser.close()

def TestService():
    print("This event occured at: ", datetime.datetime.now()) 
    while True:
        socketio.emit('connect', "TESTING DATA!")

if __name__ == '__main__':
    #t = threading.Thread(target=TestService)
    #t.start()
    print("Socket starting...")
    socketio.run(app, host='192.168.1.250')