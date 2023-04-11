import serial
from time import sleep
import numpy as np
import socketio
from datetime import datetime
from scipy.io.wavfile import write
import time
from multiprocessing import Process, Event, Condition, current_process, Manager, Value, Queue
import pymongo

# Connect to MongoDB using connection string from "mongodbKey" file
with open('mongodbKey', 'r') as file:
    MONGO_URL = file.read()
dbClient = pymongo.MongoClient(MONGO_URL)
DATABASE_NAME = "mydatabase"
COLLECTION_NAME = "AudiosTest"
  
FILE_ARRAY = []
FILE_QUEUE = Queue()
SAMPLE_RATE = 1500
ARRAY_INDEX = 0 
RECORD = Value('b', False)
SEND = False
CONDITION = Condition()
SOCKETIO = socketio.Client()
PROCESS = Process()
SERIAL = serial.Serial(port = "/dev/ttyACM0", baudrate = 921600, timeout=0)

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
        print("Recording....")
        while True:
            if not self.record.value:
                print("Stopping recording1")
                return
            else:
                val = SERIAL.readline()
                self.queue.put(val)
                sleep(0.000005)

    def run(self):
        """Default run method"""
        self.get_data()

def generateID():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print(timestamp)
    return timestamp

def insertAudio(id, wavfile):
    mycol = dbClient[DATABASE_NAME][COLLECTION_NAME]  
    f = open(wavfile, "rb")
    y= f.read()
    myInsert = { "ID": id, "fileBytes" : y}

    mycol.insert_one(myInsert)


@SOCKETIO.on('disconnect')
def disconnect_socket():
    """Handle socket disconnection"""
    print("Client disconnected")
    global RECORD
    global PROCESS
    RECORD.value = False
    if(PROCESS.is_alive()):
        PROCESS.join()
    print("Recording stopped")
    SOCKETIO.emit("SAAS-disconnect")
    #print("Thread status: ", THREAD.isAlive())

# Notification from server that recording can begin
@SOCKETIO.on('UI-record-request')
def startRecord(incoming):
    global SAMPLE_RATE
    """Start recording"""
    print(incoming)
    SOCKETIO.emit("SAAS-recording", {"samplerate":SAMPLE_RATE})
    global RECORD
    global PROCESS
    RECORD.value = True
    # Start thread
    print("Recording started")
    #print("Thread status: ", THREAD.isAlive())
    #if not THREAD.isAlive():
    PROCESS = GetSerial(FILE_QUEUE, RECORD)
    PROCESS.start()

# Notification from UI that data is ready to be sent
@SOCKETIO.on("UI-ready-for-data")
def getData():
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
        else:
            print("Invalid data: ", val)
        if len(tempArray) == 128:
            sentArray = NormalizeAudio(tempArray)
            SOCKETIO.emit("SAAS-send-data", {"vals":sentArray})
            #print("Data sent: ", tempArray)
            tempArray = []
        timeoutStart = time.time()
        while FILE_QUEUE.empty() and SEND:
            sleep(0.01)
            timeoutEnd = time.time()
            #print("Waiting for data...2", timeoutEnd)
            if timeoutEnd - timeoutStart > 5:
                break 
            
# Notification to stop recording
@SOCKETIO.on('UI-stop-request')
def stopRecording():
    """Stop recording"""
    print("Stopping recording...")
    global FILE_ARRAY
    global ARRAY_INDEX 
    global SEND
    ARRAY_INDEX = 0
    SEND = False
    global RECORD
    global PROCESS
    RECORD.value = False
    print("PID of child process: ", PROCESS.pid)

    if(PROCESS.is_alive()):
        PROCESS.join()
    print("Recording stopped")
    SOCKETIO.emit("SAAS-stopping-recording",)

    #Save list to a file:
    print("Encoding file...")
    with open("test.txt", "w") as f:
        f.write(", ".join(FILE_ARRAY))
    saveFile([int(x) for x in FILE_ARRAY], SAMPLE_RATE)
    print("File saved")

# Executes when server has connected to the UI
@SOCKETIO.on("UI-connect")
def UIConnected(data):
    """event listener for when the UI connects"""
    print("UI has connected")
    SOCKETIO.emit("SAAS-connect")
    time.sleep(1)
    print("Sending ready...")
    print(data)
    SOCKETIO.emit("SAAS-ready")
    
def saveFile(audioWaveform,sps):
    transformedSamples = NormalizeAudio(audioWaveform)
    # Scale waveform to 16-bit range
    waveform_scaled = np.int16(
        transformedSamples/np.max(np.abs(transformedSamples)) * 32767)
    id = generateID()
    filename = id + ".wav"
    # Save as WAV file using timestamp as filename
    print("Saving WAV file...")
    write(filename, sps, waveform_scaled)
    insertAudio(id, filename)
    print("File saved")
    SOCKETIO.emit("SAAS-file-saved")

def NormalizeAudio(audioWaveform):
    npAudioWaveform = np.array(audioWaveform)
    npAudioWaveform = npAudioWaveform.astype(np.float16)
    
    meanVal = sum(npAudioWaveform)/len(npAudioWaveform)
    print(npAudioWaveform)
    npAudioWaveform = np.clip(npAudioWaveform, 0, 255)

    transformedSamples = [x - meanVal for x in npAudioWaveform]
    print("Mean: ", meanVal)
    print(npAudioWaveform)

    # Clip values between -30 to 30
    return transformedSamples

if __name__ == '__main__':
    print("Connecting...")
    SOCKETIO.connect('http://192.168.1.93:5000', wait=True)
    print("Connected...")
    SOCKETIO.emit("SAAS-connect")
    time.sleep(1)
    print("Sending ready...")
    SOCKETIO.emit("SAAS-ready")
    #SOCKETIO.run(APP, host='192.168.1.250')


    