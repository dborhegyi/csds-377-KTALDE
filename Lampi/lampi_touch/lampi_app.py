import json
import pigpio
from typing import Any, Optional

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty, ColorProperty, StringProperty, ListProperty
from lampi_touch.lamp_driver import LampDriver

from kivy.properties import NumericProperty, AliasProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import paho.mqtt.client as mqtt
from paho.mqtt.client import Client, CallbackAPIVersion
import time

from lamp_common import *
import lampi_touch.lampi_util
import lampi_touch.puzzles

MQTT_CLIENT_ID = "lamp_ui"

# Throttle MQTT publishes to 20/sec max (0.05s) to prevent overwhelming
# the lamp_service with messages during rapid slider movement.
MQTT_PUBLISH_THROTTLE_SECS = 0.05

TOPIC_OUTGOING_PUZZLE_STATE_1 = "game/device1/puzzleState/received"

MQTT_CLIENT_ID = "lamp_ui"

DEVICE_NUMBER = 1

# TODO: New python file imported and called for specific puzzle handling :)


class HomeScreen(Screen):
    pass

class LampiScreen(Screen):
    pass

class AddLampiScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        #app.association_code = app.association_code

class WaitingHostScreen(Screen):
    pass

class PuzzlesScreen(Screen):
    pass

class SolvedScreen(Screen):
    pass

class P1WiresScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wires = app.puzzle_handler.puzzle_layouts[0][2]
        for i in range(4):
            wire_num = wires[i]
            color_code = {1: 'r', 4: 'g', 7: 'b', 10: 'o'}[((wire_num - 1) // 3) * 3 + 1]
            type_code = {1: 's', 2: 'w', 3: 'z'}[(wire_num - 1) % 3 + 1]
            normal = f'images/p1_wire_images/p1{color_code}{type_code}.png'
            down = f'images/p1_wire_images/p1{color_code}{type_code}c.png'
            self.ids[f'wire_{i}'].background_normal = normal
            self.ids[f'wire_{i}'].background_down = down

class P6WiresScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        if 1 in app.puzzle_handler.puzzle_layouts:
            wires = app.puzzle_handler.puzzle_layouts[0][2]
            for i in range(4):
                wire_num = wires[i]
                color_code = {1: 'r', 4: 'g', 7: 'b', 10: 'o'}[((wire_num - 1) // 3) * 3 + 1]
                type_code = {1: 's', 2: 'w', 3: 'z'}[(wire_num - 1) % 3 + 1]
                normal = f'images/p1_wire_images/p1{color_code}{type_code}.png'
                down = f'images/p1_wire_images/p1{color_code}{type_code}c.png'
                self.ids[f'wire_{i}'].background_normal = normal
                self.ids[f'wire_{i}'].background_down = down

class LampiApp(App):
    _updated: bool = False
    _updating_ui: bool = False
    _hue = NumericProperty()
    _saturation = NumericProperty()
    _brightness = NumericProperty()
    current_puzzle_state = ListProperty()
    PUZZLE_COUNT = 1
    lamp_is_on = BooleanProperty()
    # association code shenanigans
    association_code = StringProperty("")
    game_started = BooleanProperty(False)
    current_puzzle_state = []
    gameRan = StringProperty("")

    # moving between the screens!
    def go_to_lampi(self):
        self.root.current = 'lampi'

    def go_to_addlampi(self):
        self.root.current = 'addlampi'

    def go_to_waitinghost(self):
        self.root.current = 'waitinghost'

    def go_to_puzzles(self):
        self.root.current = 'puzzles'
    
    def go_to_success_screen(self):
        self.root.current = 'solved'
        time.sleep(2)
        self.go_to_puzzles()

    # all the puzzles
    def go_to_p1wires(self):
        self.puzzle_handler.wire_puzzle_config()
        self.root.current = 'p1wires'

    def go_to_p6wires(self):
        self.root.current = 'p6wires'
    def build(self):
        return Builder.load_file("lampi_touch/app.kv")
    # ==============================

    def _get_hue(self) -> float:
        return self._hue

    def _set_hue(self, value: float) -> None:
        self._hue = value

    def _get_saturation(self) -> float:
        return self._saturation

    def _set_saturation(self, value: float) -> None:
        self._saturation = value

    def _get_brightness(self) -> float:
        return self._brightness

    def _set_brightness(self, value: float) -> None:
        self._brightness = value

    hue = AliasProperty(_get_hue, _set_hue, bind=['_hue'])
    saturation = AliasProperty(_get_saturation, _set_saturation,
                               bind=['_saturation'])
    brightness = AliasProperty(_get_brightness, _set_brightness,
                               bind=['_brightness'])
    gpio17_pressed = BooleanProperty(False)
    device_associated = BooleanProperty(True)

    def on_start(self) -> None:
        self._publish_clock: Optional[Any] = None
        self.mqtt_broker_bridged: bool = False
        self._associated: bool = True
        #self.association_code: Optional[str] = None
        self.initialize_states()
        self.puzzle_handler = lampi_touch.puzzles.Puzzle_Handler()
        self.mqtt: Client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID
        )
        self.mqtt.enable_logger()
        self.mqtt.will_set(client_state_topic(MQTT_CLIENT_ID), "0",
                           qos=2, retain=True)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()
        self.set_up_gpio_and_network_status_popup()
        self.associated_status_popup = self._build_associated_status_popup()
        self.associated_status_popup.bind(on_open=self.update_popup_associated)
        Clock.schedule_interval(self._poll_associated, 0.1)
        
    # =======================
    # where the association code pops up
    def _build_associated_status_popup(self):
        return Popup(title='Associate your Lamp',
                     content=Label(text='Msg here', font_size='30sp'),
                     size_hint=(1, 1), auto_dismiss=False)

    def on_hue(self, instance: Any, value: float) -> None:
        if self._updating_ui:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), MQTT_PUBLISH_THROTTLE_SECS)

    def on_saturation(self, instance: Any, value: float) -> None:
        if self._updating_ui:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), MQTT_PUBLISH_THROTTLE_SECS)

    def on_brightness(self, instance: Any, value: float) -> None:
        if self._updating_ui:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), MQTT_PUBLISH_THROTTLE_SECS)

    def on_lamp_is_on(self, instance: Any, value: bool) -> None:
        if self._updating_ui:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), MQTT_PUBLISH_THROTTLE_SECS)
    
    def submit_partner_puzzle(self):
        payload = {'h': self.hue, 's': self.saturation, 'b': self.brightness}
        topic = f"game/{get_device_id()}/puzzleState/sent"
        self.mqtt.publish(topic, json.dumps(payload), qos=1)

    def on_connect(self, client: Client, userdata: Any,
                   flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode,
                   properties: Optional[mqtt.Properties]) -> None:
        self.mqtt.publish(client_state_topic(MQTT_CLIENT_ID), b"1",
                          qos=2, retain=True)
        self.mqtt.message_callback_add(TOPIC_LAMP_CHANGE_NOTIFICATION,
                                       self.receive_new_lamp_state)
        self.mqtt.message_callback_add(broker_bridge_connection_topic(),
                                       self.receive_bridge_connection_status)
        self.mqtt.message_callback_add(device_association_topic(),
                                       self.receive_associated)
        self.mqtt.subscribe(broker_bridge_connection_topic(), qos=1)
        self.mqtt.subscribe(TOPIC_LAMP_CHANGE_NOTIFICATION, qos=1)
        self.mqtt.subscribe(device_association_topic(), qos=2)

        self.mqtt.message_callback_add(TOPIC_INCOMING_PUZZLE_STATE.replace("{{device_id}}", get_device_id()), self.receive_new_puzzle_state)
        self.mqtt.subscribe(TOPIC_INCOMING_PUZZLE_STATE.replace("{{device_id}}", get_device_id()), qos=1)
        self.mqtt.message_callback_add(TOPIC_GAME_STARTED.replace("{{device_id}}", get_device_id()), self.receive_game_started)
        #self.mqtt.subscribe(TOPIC_GAME_STARTED.replace("{{device_id}}", get_device_id()), qos=1)
        self.mqtt.message_callback_add("game/state", self.receive_game_state)
        self.mqtt.message_callback_add("gameStarted", self.receive_game_started)
        self.mqtt.subscribe("gameStarted", qos=1)

    def _poll_associated(self, dt):
        # this polling loop allows us to synchronize changes from the
        #  MQTT callbacks (which happen in a different thread) to the
        #  Kivy UI
        self.device_associated = self._associated

    def receive_associated(self, client, userdata, message):
        # this is called in MQTT event loop thread
        new_associated = json.loads(message.payload.decode('utf-8'))

        if self._associated != new_associated['associated']:
            if not new_associated['associated']:
                self.association_code = new_associated['code'][0:6]
            else:
                self.association_code = ""
            self._associated = new_associated['associated']

    def on_device_associated(self, instance, value):
        #if value:
        #    self.associated_status_popup.dismiss()
        #else:
        #    self.associated_status_popup.open()
        pass

    
    def initialize_states(self):
        self.current_puzzle_state = ['N', 'N']

    #THIS IS DIFFERENT between each lampi...
    def publish_puzzle_state(self):
        self.mqtt.publish(TOPIC_OUTGOING_PUZZLE_STATE_1, self.current_puzzle_state, qos=1)
    
    def publish_partner_puzzle_state(self, information):
        TOPIC_PARTNER_PUZZLE_STATE.replace("{{device_id}}", get_device_id())
        self.mqtt.publish(TOPIC_PARTNER_PUZZLE_STATE.replace("{{device_id}}", get_device_id()), information, qos=1)
        return

    # Updates the puzzle state at index to given state
    # Publishes new state to mqtt (evaluate logic later)
    def update_puzzle_state(self, puzzle_index: int, new_state: str, publish: bool):
        if puzzle_index < 0 or puzzle_index >= self.PUZZLE_COUNT:
            print("Index out of bounds: " + str(puzzle_index))
            return
        self.current_puzzle_state[puzzle_index] = new_state
        if not publish:
            return
        self.publish_puzzle_state()

    # Resets puzzle state at a point to not solved
    def reset_puzzle_state(self, puzzle_index: int):
        self.update_puzzle_state(puzzle_index, 'N', True)


    def on_cut_wire(self, position: int) -> None:
        if not hasattr(self, 'puzzle_handler'):
            return
        result = self.puzzle_handler.solve_wire_puzzle(position)
        if result == 1:
            self.update_puzzle_state(0, 'S', False)  # Temporarily disable publish to avoid crash
        else:
            self.update_puzzle_state(0, 'F', False)
        # Update the UI to show the cut wire
        screen = self.root.current_screen
        if hasattr(screen, 'ids') and f'wire_{position}' in screen.ids:
            wire_button = screen.ids[f'wire_{position}']
            wire_button.background_normal = wire_button.background_down
        time.sleep(1)



    def on_led_puzzle_solve(self, sliderValue: float):
        ##this would be the single player puzzle solve...
        if not hasattr(self, 'puzzle_handler'):
            return
        result = self.puzzle_handler.solve_led_puzzle(sliderValue, DEVICE_NUMBER)
        if result == 1:
            self.update_puzzle_state(0, 'S', True)
        else:
            self.update_puzzle_state(0, 'F', True)

    # def on_partner_led_solve(self, color: float, saturation: float, brightness: float):
    #     #publish state onto partner receiving end
    #     if not hasattr(self, 'puzzle_handler') or 2 not in self.puzzle_handler.puzzle_layouts:
    #         return
    #     result = self.puzzle_handler.solve_led_puzzle(color, saturation, brightness)
    #     return


    def _process_incoming_puzzle_state(self, payload: str) -> None:
        payload = payload.strip()
        if not payload:
            return

        states = payload.split(',')

        updated = False
        for idx, state in enumerate(states):
            if idx >= self.PUZZLE_COUNT or state not in ('N', 'P', 'S', 'F'):
                continue
            if self.current_puzzle_state[idx] != state:
                self.current_puzzle_state[idx] = state
                updated = True
        if updated:
            print(f"Updated puzzle states: {self.current_puzzle_state}")

    def get_wire_description(self, position: int) -> str:
        if 1 not in self.puzzle_handler.puzzle_layouts:
            return "ERROR: Wire puzzle not detected."
        wires = self.puzzle_handler.puzzle_layouts[1][2]
        if position >= len(wires):
            return f"Wire {position}"
        wire_num = wires[position]
        color_map = {1: 'Red', 4: 'Green', 7: 'Blue', 10: 'Orange'}
        shape_map = {1: 'Straight', 2: 'Squiggly', 3: 'Zigzag'}
        color = color_map.get((wire_num - 1) // 3 * 3 + 1, 'Unknown')
        shape = shape_map.get((wire_num - 1) % 3 + 1, 'Unknown')
        return f"{color} {shape}"

    def receive_game_started(self, client: Client, userdata: Any,
                             message: mqtt.MQTTMessage) -> None:
        gameRan = "YES IT DID!!"
        Clock.schedule_once(lambda dt: self.start_game(), 0.01)

    def start_game(self):
        self.game_started = True
        self.initialize_states()
        # Generate wire puzzle layout
        self.puzzle_handler.wire_puzzle_config()

    
    def update_popup_associated(self, instance):
        pass
    #     code = self.association_code[0:6]
    #     instance.content.text = ("Please use the\n"
    #                              "following code\n"
    #                              "to associate\n"
    #                              "your device\n"
    #                              f"on the Web\n{code}")

    def explode():
        #run through explosion sequence.
        pass

    def receive_game_state(self, client: Client, userdata: Any,
                           message: mqtt.MQTTMessage):
        if(message.payload == 1):
            #1 = EXPLODED
             explode()
             
        

    def receive_bridge_connection_status(self, client: Client, userdata: Any,
                                         message: mqtt.MQTTMessage) -> None:
        # monitor if the MQTT bridge to our cloud broker is up
        if message.payload == b"1":
            self.mqtt_broker_bridged = True
        else:
            self.mqtt_broker_bridged = False

    def receive_new_lamp_state(self, client: Client, userdata: Any,
                               message: mqtt.MQTTMessage) -> None:
        new_state = json.loads(message.payload.decode('utf-8'))
        Clock.schedule_once(lambda dt: self._update_ui(new_state), 0.01)

    
    #Processes new puzzle state from Django    
    def receive_new_puzzle_state(self, client: Client, userdata: Any,
                                 message: mqtt.MQTTMessage) -> None:
        payload = message.payload.decode('utf-8')
        Clock.schedule_once(lambda dt: self._process_incoming_puzzle_state(payload), 0.01)

    def _update_ui(self, new_state: dict[str, Any]) -> None:
        """Update UI from MQTT state.

        Ignores updates from ourselves (except the first one for initial sync)
        to prevent MQTT feedback loops from causing UI jumpiness.
        """
        if self._updated and new_state.get('client') == MQTT_CLIENT_ID:
            # ignore updates generated by this client, except the first to
            #   make sure the UI is synchronized with the lamp_service
            return
        self._updating_ui = True
        try:
            if 'color' in new_state:
                self.hue = new_state['color']['h']
                self.saturation = new_state['color']['s']
            if 'brightness' in new_state:
                self.brightness = new_state['brightness']
            if 'on' in new_state:
                self.lamp_is_on = new_state['on']
        finally:
            self._updating_ui = False
        self._updated = True

    def _update_leds(self) -> None:
        msg = {'color': {'h': self._hue, 's': self._saturation},
               'brightness': self._brightness,
               'on': self.lamp_is_on,
               'client': MQTT_CLIENT_ID}
        self.mqtt.publish(TOPIC_SET_LAMP_CONFIG,
                          json.dumps(msg).encode('utf-8'),
                          qos=1)
        self._publish_clock = None

    def set_up_gpio_and_network_status_popup(self) -> None:
        """Set up a popup to display the Lampi's IP
        address when a button is pressed."""
        self.pi: pigpio.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_gpio, 0.05)
        self.network_status_popup: Popup = self._build_network_status_popup()
        self.network_status_popup.bind(on_open=self.update_popup_ip_address)

    def _build_network_status_popup(self) -> Popup:
        return Popup(title='Network Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_popup_ip_address(self, instance: Popup) -> None:
        """Update the popup with the current IP address"""
        interface = "wlan0"
        ipaddr = lampi_touch.lampi_util.get_ip_address(interface)
        deviceid = lampi_touch.lampi_util.get_device_id()
        msg = f"{interface}: {ipaddr}\nDeviceID: {deviceid}" + \
            f"\nBroker Bridged: {self.mqtt_broker_bridged}"
        instance.content.text = msg

    def on_gpio17_pressed(self, instance: Any, value: bool) -> None:
        """Open or close the popup depending on the provided value"""
        if value:
            self.network_status_popup.open()
        else:
            self.network_status_popup.dismiss()

    def _poll_gpio(self, _delta_time: float) -> None:
        # GPIO17 is the rightmost button when looking front of LAMPI
        self.gpio17_pressed = not self.pi.read(17)
