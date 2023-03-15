import random

class TestValues:
    values = {
        'frequency':[],
        'volume':[]
    }
    def __init__(self, numVals:int,freq:bool=True,volume:bool=True):
        freqs = []
        vols = []
        for i in range(numVals):
            if(freq and volume):
                freqs.append(random.randint(20, 2000)) 
                vols.append(random.randint(1,100))
            elif(freq):
                freqs.append(random.randint(20, 2000)) 
            elif(volume):
                vols.append(random.randint(1,100))

    def getVals(self):

        return self.values

            
