import serial
import time

class SerialService:


    def retrieveData():
        ack = ""

        ser = serial.Serial('COM6', 9600, timeout=0)
        ser.write("Req".encode())
        timeout = time.time()
        while (not ack.find("Ack")) or ((time.time() - timeout) >= 10.000):
            ack += ser.read().decode()
            if (time.time() - timeout) >= 10.000:
                
        
        output = []
        while(1):
            current = ser.read().decode()

            if(current != '\n' or '\r'): 
                output.append(current)
            else:
                print(", ".join(output))
                output =[]


