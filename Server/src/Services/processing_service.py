import numpy as np
import scipy.fft as fft
import matplotlib.pyplot as plt
from datetime import timedelta
from functools import reduce

#source: https://www.alphabold.com/fourier-transform-in-python-vibration-analysis/
class ProcessingService:

    @staticmethod
    def ProcessAudio(inputSamples: list, sampleTime: timedelta, samplingFrequency: int = 2048):
        meanVal = reduce(lambda a, b: a + b, inputSamples)/len(inputSamples)
        transformedSamples = [x - meanVal  for x in inputSamples]

        x = np.fft.rfft(transformedSamples)
        #freqVals = np.fft.rfftfreq(len(inputSamples), d=1./sampleRate)

        freqVals = np.fft.rfftfreq(len(transformedSamples), d=((1.0 / (samplingFrequency-600))))
        intensityVals = np.abs(x)
        #print(transformedSamples)
        # print(freqVals)
        # print(intensityVals)

        return freqVals, intensityVals
        plt.plot(freqVals[0:len(freqVals)], intensityVals[0:len(intensityVals)])
        plt.xlabel("frequency Hz")
        plt.ylabel("Amplitude, units") 
        plt.show()

        