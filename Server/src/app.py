from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from Testing.test_values import TestValues
from Services.serial_service import SerialService
from Services.processing_service import ProcessingService

app = Flask(__name__)
socketio = SocketIO(app)

values = TestValues(20000).getVals()

# @app.route('/')
# def index():
#     return render_template('Webhook\index.html',**values)

@socketio.on('connect')
def test_connect():
    emit('after connect', {'data':values})

@socketio.on('Slider value changed')
def value_changed(message):
    values[message['who']] = message['data']
    emit('update value', message, broadcast=True)


if __name__ == '__main__':
    returnedSamples = SerialService.RetrieveDataTest(115200, 128)

    #ProcessingService.ProcessAudio(returnedSamples)

    #print(values)
    
    #socketio.run(app, host='0.0.0.0')