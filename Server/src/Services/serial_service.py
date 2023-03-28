import serial
from time import sleep
from Services.processing_service import ProcessingService
from threading import Thread
from datetime import datetime
import matplotlib.pyplot as plt
from flask_socketio import SocketIO, emit



class SerialService:


    def __init__(self, port, baudRate, socket):
        self.THREAD = Thread()
        self.port = port
        self.delay = 1
        self.baudRate = baudRate
        self.ser = serial.Serial(port = port, baudrate = baudRate, timeout=0)
        self.socket = socket




    def RetrieveData(self):
        outputSamples = []
        counter = 0
        while counter < 128:
            val = self.ser.readline()
            sleep(.005)
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
                        if(parsedVal > 700) or (parsedVal < 200):
                            parsedVal = 240
                        else:
                        #print(float(val))
                            outputSamples.append(float(parsedVal))
                        counter += 1
        self.socket.emit('test', {'test':outputSamples})
        sleep(self.delay)

    def run(self):
        self.RetrieveData()

