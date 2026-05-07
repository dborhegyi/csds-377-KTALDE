import paho.mqtt.client as mqtt
import time
import json

class WinningSequence:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect("localhost", 1883)

    def _set_color(self, h, s, b, on=True):
        msg = {
            'color': {'h': h, 's': s},
            'brightness': b,
            'on': on,
            'client': 'winning_sequence'
        }
        self.client.publish("lamp/set_config", json.dumps(msg), qos=1)

    def run(self):
        try:
            while True:
                self._set_color(0, 0, 0, on=False)
                time.sleep(0.25)
                # Flash green (hue ~0.33)
                self._set_color(0.33, 1.0, 1.0, on=True)
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._set_color(0, 0, 0, on=False)
        self.client.disconnect()