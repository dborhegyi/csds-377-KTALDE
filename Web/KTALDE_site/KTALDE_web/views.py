from typing import Any, Dict
from django.views import generic
from django.shortcuts import render
import json
import paho.mqtt.client as mqtt

class StartGameView(generic.TemplateView):
    template_name = 'KTALDE_web/startgame.html'

def ingame(request):
    return render(request, 'KTALDE_web/ingame.html')

def gameover(request):
    return render(request, 'KTALDE_web/gameover.html')

def win(request):
    return render(request, 'KTALDE_web/win.html')

def start_partner_matching_game(request):
    # Publish game start to device_1
    publish_partner_game_start()
    
    return render(request, 'KTALDE_web/ingame.html')

# def view_pdf(request):
#     try:
#         # Build an absolute path relative to this views.py file
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         file_path = os.path.join(base_dir, 'static', 'KTALDE_web', 'pdf', 'ExpertInstructions.pdf')
#         return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
#     except FileNotFoundError:
#         raise Http404("PDF not found")


# MQTT Handling
MQTT_CLIENT_ID = "django_server"

# Hardcoded devices
DEVICE_1 = "device_1"
DEVICE_2 = "device_2"

# Hardcoded display colors and targets
DISPLAY_COLORS = {
    DEVICE_1: {'h': 0.25, 's': 1.0, 'b': 1.0},  # yellow
    DEVICE_2: {'h': 0.58, 's': 1.0, 'b': 1.0}   # blue
}

TARGET_RANGES = {
    DEVICE_1: {'h': (0.7, 0.8), 's': (0.7, 1.0), 'b': (0.7, 1.0)},  # purple
    DEVICE_2: {'h': (0.0, 0.1), 's': (0.7, 1.0), 'b': (0.7, 1.0)}   # red
}

# In-memory game state
game_states = {
    DEVICE_1: None,  # {'h': float, 's': float, 'b': float}
    DEVICE_2: None
}

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode('utf-8'))
    
    if topic == f"game/{DEVICE_1}/puzzleState/sent":
        game_states[DEVICE_1] = payload
    elif topic == f"game/{DEVICE_2}/puzzleState/sent":
        game_states[DEVICE_2] = payload
    
    # Check if both submitted
    if game_states[DEVICE_1] and game_states[DEVICE_2]:
        # Validate
        match_1 = (
            TARGET_RANGES[DEVICE_1]['h'][0] <= game_states[DEVICE_1]['h'] <= TARGET_RANGES[DEVICE_1]['h'][1] and
            TARGET_RANGES[DEVICE_1]['s'][0] <= game_states[DEVICE_1]['s'] <= TARGET_RANGES[DEVICE_1]['s'][1] and
            TARGET_RANGES[DEVICE_1]['b'][0] <= game_states[DEVICE_1]['b'] <= TARGET_RANGES[DEVICE_1]['b'][1]
        )
        match_2 = (
            TARGET_RANGES[DEVICE_2]['h'][0] <= game_states[DEVICE_2]['h'] <= TARGET_RANGES[DEVICE_2]['h'][1] and
            TARGET_RANGES[DEVICE_2]['s'][0] <= game_states[DEVICE_2]['s'] <= TARGET_RANGES[DEVICE_2]['s'][1] and
            TARGET_RANGES[DEVICE_2]['b'][0] <= game_states[DEVICE_2]['b'] <= TARGET_RANGES[DEVICE_2]['b'][1]
        )
        
        if match_1 and match_2:
            client.publish("game/state", "win")
        else:
            client.publish("game/state", "exploded")
        
        # Reset
        game_states[DEVICE_1] = None
        game_states[DEVICE_2] = None

# Setup MQTT client (call this in app startup, e.g., in apps.py)
mqtt_client = None

def setup_partner_mqtt():
    global mqtt_client
    from django.conf import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID
        )
        mqtt_client.on_message = on_message
        mqtt_client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
        mqtt_client.subscribe(f"game/{DEVICE_1}/puzzleState/sent")
        mqtt_client.subscribe(f"game/{DEVICE_2}/puzzleState/sent")
        mqtt_client.loop_start()
        logger.info("MQTT client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MQTT client: {e}")
        mqtt_client = None

def publish_partner_game_start():
    # Publish display colors
    for device, color in DISPLAY_COLORS.items():
        payload = {'color': color}
        mqtt_client.publish(f'game/{device}/gameStarted', json.dumps(payload))
