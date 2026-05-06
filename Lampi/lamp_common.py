import paho.mqtt.client

DEVICE_ID_FILENAME = '/sys/class/net/eth0/address'

# MQTT Topic Names
TOPIC_SET_LAMP_CONFIG: str = "lamp/set_config"
TOPIC_LAMP_CHANGE_NOTIFICATION: str = "lamp/changed"
TOPIC_LAMP_ASSOCIATED: str = "lamp/associated"
TOPIC_OUTGOING_PUZZLE_STATE: str = "game/{{device_id}}/puzzleState/received"
TOPIC_INCOMING_PUZZLE_STATE: str = "game/{{device_id}}/puzzleState/sent"
TOPIC_GAME_STARTED: str = "game/{{device_id}}/gameStarted"
# once we know how this is happening.. TOPIC_PARTNER_PUZZLE_INFO: str= ""

def get_device_id() -> str:
    mac_addr = open(DEVICE_ID_FILENAME).read().strip()
    return mac_addr.replace(':', '')


def client_state_topic(client_id: str) -> str:
    return 'lamp/connection/{}/state'.format(client_id)


def broker_bridge_connection_topic() -> str:
    device_id = get_device_id()
    return '$SYS/broker/connection/{}_broker/state'.format(device_id)


# Is this over websockets? Looks like it's manual connection.
# MQTT Broker Connection info
MQTT_VERSION: int = paho.mqtt.client.MQTTv311
MQTT_BROKER_HOST: str = "ec2-32-194-170-233.compute-1.amazonaws.com"
MQTT_BROKER_PORT: int = 50001 # originally 50002, try changing to 50001 to be able to sub on it
MQTT_BROKER_KEEP_ALIVE_SECS: int = 60
