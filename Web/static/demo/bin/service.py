#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from paho.mqtt.client import Client
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.properties import Properties
from typing import Any, Optional
import json
import sys
import time


PORT: int = 50001

configuration: dict[str, Any] = {}
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def on_connect(client: Client, userdata: Any, flags: mqtt.ConnectFlags,
               reason_code: ReasonCode,
               properties: Optional[Properties]) -> None:
    print("... connected")

    print("connection result: ")
    print(reason_code)


def on_disconnect(client: Client, userdata: Any,
                  disconnect_flags: mqtt.DisconnectFlags,
                  reason_code: ReasonCode,
                  properties: Optional[Properties]) -> None:
    print("... disconnected")


def go() -> None:
    i = 0
    while True:
        if i == sys.maxsize:
            i = 0

        message = json.dumps(configuration)
        print("message: " + message)
        configuration['value'] = i
        client.publish("devices/DEMO/label/changed",
                       payload=json.dumps(configuration))
        i += 1
        time.sleep(1)


if __name__ == "__main__":
    client.on_connect = on_connect
    print("... set connection listener")

    client.on_disconnect = on_disconnect
    print("... set disconnection listener")

    client.connect('localhost', port=PORT, keepalive=60)
    print("... tried to connect")

    client.loop_start()
    print("... starting client loop")

    go()
