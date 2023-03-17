import numpy as np
import scipy.fft as fft
import matplotlib.pyplot as plt

#source: https://www.alphabold.com/fourier-transform-in-python-vibration-analysis/
class ProcessingService:

    @staticmethod
    def ProcessAudio(inputSamples: list, sampleRate: int = 2048):
        print("Begin...")
        x = np.fft.rfft(inputSamples)
        #freqVals = np.fft.rfftfreq(len(inputSamples), d=1./sampleRate)
        freqVals = np.fft.rfftfreq(len(inputSamples), d=1./1600)
        intensityVals = np.abs(x)
        plt.plot(freqVals[1:2048], intensityVals[1:2048])
        plt.xlabel("frequency Hz")
        plt.ylabel("Amplitude, units")
        plt.show()
