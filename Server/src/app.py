from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from Testing.testvalues import TestValues
from Services.serialService import SerialService

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
    SerialService.retrieveData()

    #print(values)
    
    #socketio.run(app, host='0.0.0.0')