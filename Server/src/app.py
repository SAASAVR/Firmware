from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from Testing.test_values import TestValues
from Services.serial_service import SerialService
from Services.processing_service import ProcessingService
import threading

outputSamples = []
app = Flask(__name__)
socketio = SocketIO(app)

values = TestValues(20000).getVals()

@app.route('/')
def index():
    return render_template('index.html',**values)

@socketio.on('connect')
def test_connect():
    print('Client connected')
    
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('test')
def value_changed(message):
    values[message['who']] = message['data']
    emit('update value', message, broadcast=True)

def RunService():
    try:
        serialService = SerialService("/dev/ttyACM0", 115200, socketio)
    except:
         serialService = SerialService("/dev/ttyACM1", 115200, socketio)

    outputSamples = serialService.RetrieveData()
    #freqVals, intensityVals = ProcessingService.ProcessAudio(outputSamples)
    serialService.ser.close()

def TestService():
    print("Testing service")
    while True:
        socketio.emit('test', "TESTING DATA!", namespace='/test')

if __name__ == '__main__':

    t = threading.Thread(target=TestService)
    t.start()
    print("Socket starting...")
    socketio.run(app, host='localhost')