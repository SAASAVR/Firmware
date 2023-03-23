import serial
import time
from Services.processing_service import ProcessingService
import threading
from datetime import datetime
import matplotlib.pyplot as plt
from flask_socketio import SocketIO, emit

class SerialService:


    def __init__(self, port, baudRate, socket):
        self.port = port
        self.baudRate = baudRate
        self.ser = serial.Serial(port = port, baudrate = baudRate, timeout=0)
        self.socket = socket


    def RetrieveData(self):
        freqVals = range(128)
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot()
        line1, = ax.plot(range(0, 800))
        fig.show()
        print("retreiving data in thread...")

        while 1: 
            counter = 0
            outputSamples = []
            while counter < 128:
                val = self.ser.readline()
                if val != b'':
                    try:
                        if(float(val.decode().strip()) > 0):
                            #print(float(val))
                            outputSamples.append(float(val))
                            counter += 1
                    # #serialThread.start()
                    except:
                        parsedVal = float(val.decode().strip().split(".")[0])
                        if(parsedVal > 0):
                            #print(float(val))
                            outputSamples.append(float(parsedVal))
                            counter += 1
            return outputSamples
            
            data = {'freqVals': freqVals, 'intensityVals': intensityVals}
            self.socket.emit('data', data, namespace='/data')
            #print(freqVals)
            #print(intensityVals)
            line1.set_xdata(freqVals[0:len(freqVals)])
            line1.set_ydata(intensityVals[0:len(intensityVals)])
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.1)
            

