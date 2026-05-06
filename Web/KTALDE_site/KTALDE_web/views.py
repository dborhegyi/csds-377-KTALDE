from typing import Any, Dict
from django.views import generic
from django.shortcuts import get_object_or_404, render
from .models import Lampi, Game
from django.http import FileResponse, Http404
import os
import uuid
import random
import json
import paho.mqtt.client as mqtt
from django.db import models

class StartGameView(generic.TemplateView):
    template_name = 'KTALDE_web/startgame.html'

def ingame(request):
    return render(request, 'KTALDE_web/ingame.html')

def gameover(request):
    return render(request, 'KTALDE_web/gameover.html')

def win(request):
    return render(request, 'KTALDE_web/win.html')

def start_partner_matching_game(request):
    # Get lampis from request (e.g., ?display_lampi_id=...&match_lampi_id=...)
    display_lampi = Lampi.objects.get(device_id=request.GET['display_lampi_id'])
    match_lampi = Lampi.objects.get(device_id=request.GET['match_lampi_id'])
    
    game_id = str(uuid.uuid4())
    # Generate random target color (HSB)
    target_color = {
        'h': random.uniform(0, 1),
        's': random.uniform(0, 1),
        'b': random.uniform(0, 1)
    }
    
    game = Game.objects.create(
        game_id=game_id,
        display_lampi=display_lampi,
        match_lampi=match_lampi,
        target_color=target_color,
        status='active'
    )
    
    # Publish game start
    publish_partner_game_start(game)
    
    return render(request, 'KTALDE_web/ingame.html', {'game': game})

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

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode('utf-8'))
    
    # Parse topic: game/{device_id}/puzzleState/sent
    parts = topic.split('/')
    if len(parts) >= 4 and parts[0] == 'game' and parts[3] == 'puzzleState':
        device_id = parts[1]
        # Find active game involving this device
        game = Game.objects.filter(
            (models.Q(display_lampi__device_id=device_id) | models.Q(match_lampi__device_id=device_id)),
            status='active'
        ).first()
        if game:
            if game.display_lampi.device_id == device_id:
                game.display_state = payload
                game.display_submitted = True
            elif game.match_lampi.device_id == device_id:
                game.match_state = payload
                game.match_submitted = True
            game.save()
            
            if game.display_submitted and game.match_submitted:
                # Validate match
                match_h = abs(game.match_state.get('h', 0) - game.target_color['h']) < 0.1  # Tolerance
                match_s = abs(game.match_state.get('s', 0) - game.target_color['s']) < 0.1
                match_b = abs(game.match_state.get('b', 0) - game.target_color['b']) < 0.1
                is_match = match_h and match_s and match_b
                
                game.winner = 'match' if is_match else None
                game.status = 'completed'
                game.save()
                
                # Publish results
                result = {'match': is_match}
                client.publish(f'game/{game.display_lampi.device_id}/partnerPuzzleStates', json.dumps(result))
                client.publish(f'game/{game.match_lampi.device_id}/partnerPuzzleStates', json.dumps(result))

# Setup MQTT client (call this in app startup, e.g., in apps.py)
mqtt_client = None

def setup_partner_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 50002)
    mqtt_client.subscribe("game/+/puzzleState/sent")
    mqtt_client.loop_start()

def publish_partner_game_start(game):
    # Publish target color to display lampi's gameStarted topic
    payload = {'color': game.target_color}
    mqtt_client.publish(f'game/{game.display_lampi.device_id}/gameStarted', json.dumps(payload))