import serial
import time
from Services.processing_service import ProcessingService

class SerialService:
    @staticmethod
    def TestInput(baudRate):
        outputSamples = []
        ser = serial.Serial('/dev/ttyACM0', baudRate, timeout=0)
        while(1):
            val = ser.readline().decode().strip()
            if(len(val) > 1):
                if(float(val) > 0):
                    print(float(val))
                
        
    @staticmethod
    def RetrieveDataTest(baudRate, samples):
        ser = serial.Serial('/dev/ttyACM1', baudRate, timeout=0)
        #while 1: 
        outputSamples = []
        counter = 0
        while counter < samples: 
            val = ser.readline().decode().strip()
            if(len(val) > 1):
                if(float(val) > 0):
                    outputSamples.append(float(val))
                    counter += 1
        ProcessingService.ProcessAudio(outputSamples)