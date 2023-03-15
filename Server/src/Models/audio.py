class Audio :
    snippet = {
        "Frequencies": {    # List assigned to each frequency corresponds
        "100Hz": [],        # to the intensity of each frequency at a given
        "200Hz": [],        # moment.
        "300Hz": [],
        "400Hz": [],        # I think I'm focusing too much on user interaction even though the user will never see this part of the product.
        "500Hz": [],
        "600Hz": [],
        "700Hz": [],
        "800Hz": [],
        "900Hz": [],
        "1000Hz": []
        },
        "SampleRate": 128   # measured in samples/s

    }
    def __init__(self, sampleRate : int):
        self.snippet["SampleRate"] = sampleRate



 


