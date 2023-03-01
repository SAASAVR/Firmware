// Large portion of code by Arik Yavilevich from blog.yavilevich.com
//(https://blog.yavilevich.com/2016/08/arduino-sound-level-meter-and-spectrum-analyzer/)
// File used to test Aruduino microphone inputs.
#define MicSamples (1024 * 2)
#define MicPin A0
char im[128], data[128];
char x = 0, ylim = 60;
int i = 0, val;
//==============================================================
void setup()
{
    Serial.begin(9600);
    analogReference(DEFAULT);
}

void loop()
{
    MeasureAnalog();
}

void MeasureAnalog()
{
    long signalAvg = 0, signalMax = 0, signalMin = 1024, t0 = millis();
    for (int i = 0; i < MicSamples; i++)
    {
        int k = analogRead(MicPin);
        signalMin = min(signalMin, k);
        signalMax = max(signalMax, k);
        signalAvg += k;
    }
    signalAvg /= MicSamples;

    // print
    Serial.print("Time: " + String(millis() - t0));
    Serial.print(" Min: " + String(signalMin));
    Serial.print(" Max: " + String(signalMax));
    Serial.print(" Avg: " + String(signalAvg));
    Serial.print(" Span: " + String(signalMax - signalMin));
    Serial.print(", " + String(signalMax - signalAvg));
    Serial.print(", " + String(signalAvg - signalMin));
    Serial.println("");
}
