import serial
from time import sleep
import numpy as np
import socketio
from datetime import datetime
import io
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import time
from multiprocessing import Process, Event, Condition, current_process, Manager, Value, Queue
import pymongo
import math
import librosa

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

"""Convert the 'Bytefile to a numpy float"""
def binaryData2numpy(input):
    out, sr = librosa.load(io.BytesIO(input), sr=None)
    return out

"""changes the numpy array to a mel spectrum image in binary"""
def generateMelSpecBinaryImage(np_array):
    # np_array, sr = librosa.load("hoot-46198.mp3", sr=22050)
    S = librosa.feature.melspectrogram(y=np_array,
                                  sr=22050,
                                  n_mels=128 * 2,)

    S_db_mel = librosa.amplitude_to_db(S, ref=np.max)
    spectrumList = S_db_mel.tolist()
    fig, ax = plt.subplots(figsize=(10, 5))
    # Plot the mel spectogram
    img = librosa.display.specshow(S_db_mel,
                                x_axis='time',
                                y_axis='log',
                                ax=ax)
    ax.set_title('Mel Spectogram', fontsize=20)
    fig.colorbar(img, ax=ax, format=f'%0.2f')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    data = buf.getvalue()
    buf.close()
    return data
"""Initial insert of audio to database, contains ID, the audio data in binary, sampling rate(sr), an image of mel spectrum"""
def insertAudio(id, wavfile, sr, size = 10000):
    mycol = dbClient[DATABASE_NAME][COLLECTION_NAME]
    f = open(wavfile, "rb")
    y= f.read()
    binaryImg = generateMelSpecBinaryImage(binaryData2numpy(y))
    myInsert = {"ID": id, "fileBytes" : y, "AudioData":{'sr': sr, 'Size':size, 'clipLength': size/sr, 'MelSpectrumImgBytes': binaryImg}, "MLData":{}}
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
            normalizedArray = NormalizeAudio(tempArray)
            SOCKETIO.emit("SAAS-send-data", {"vals":normalizedArray})
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
    SOCKETIO.emit("SAAS-ready")
    
def saveFile(audioWaveform,sps):
    global FILE_ARRAY
    transformedSamples = NormalizeAudio(audioWaveform)
    # Scale waveform to 16-bit range
    waveform_scaled = np.int16(
        transformedSamples/np.max(np.abs(transformedSamples)) * 32767)
    id = generateID()
    filename = id + ".wav"
    # Save as WAV file using timestamp as filename
    print("Saving WAV file...")
    write(filename, sps, waveform_scaled)
    insertAudio(id, filename, sps)
    print("File saved")
    FILE_ARRAY = []
    SOCKETIO.emit("SAAS-file-saved")

def NormalizeAudio(audioWaveform):
    npAudioWaveform = np.array(audioWaveform)
    npAudioWaveform = npAudioWaveform.astype(np.float16)
    
    meanVal = sum(npAudioWaveform)/len(npAudioWaveform)
    npAudioWaveform = np.clip(npAudioWaveform, 0, 255)

    transformedSamples = [(x - meanVal)/meanVal for x in npAudioWaveform]

    # Clip values between -30 to 30
    return transformedSamples


if __name__ == '__main__':
    print("Connecting...")
    SOCKETIO.connect('http://192.168.186.208:5000', wait=True)
    print("Connected...")
    SOCKETIO.emit("SAAS-connect")
    time.sleep(1)
    print("Sending ready...")
    SOCKETIO.emit("SAAS-ready")
    #SOCKETIO.run(APP, host='192.168.1.250')


    