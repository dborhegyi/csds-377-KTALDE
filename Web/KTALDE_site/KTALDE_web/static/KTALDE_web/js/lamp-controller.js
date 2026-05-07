/**
 * LAMPI Web Controller (Django Version)
 *
 * This module implements the Alpine.js component that controls the LAMPI
 * smart lamp through MQTT over WebSockets.
 *
 * Configuration is passed from Django via window.LAMPI_CONFIG
 */

// import mqtt from 'mqtt';
// import { hsbToHex, darkenHex } from './color-utils.js';

// ============================================================================
// Configuration Constants (from Django)
// ============================================================================

// Get configuration from Django template
// Django provides: deviceId, mqtt settings, and complete MQTT topic strings
const CONFIG = window.LAMPI_CONFIG || {};
const HOST_ADDRESS = CONFIG.mqtt?.hostname || window.location.hostname;
const HOST_PORT = CONFIG.mqtt?.websocketsPort || 50002;

// Generate a unique client ID to identify this browser session
const CLIENT_ID = Math.random().toString(36).substring(2) + '_web_client';

// MQTT topics are provided by Django - no client-side topic synthesis needed
// CONFIG.topics contains: setConfig, lampChanged, lampServiceState, lampUIState

// ============================================================================
// Alpine.js Component Definition
// ============================================================================

//TODO: Need a CONFIG.topics.pubPuzzleState topic to pub state FROM Django TO Lampi
//TODO: Need CONFIG.topics.timer for publishing timer state
//TODO: Need CONFIG.topics.gameState to tell lampis what is happening with the game.

/**
 * Creates the lamp controller Alpine.js component
 */
function lampController() {
  return {
    // ========================================================================
    // Reactive State Properties
    // ========================================================================

    // Lamp state (0.0 to 1.0 for sliders, boolean for power)
    hue: 0.5,
    saturation: 0.5,
    brightness: 0.5,
    on: true,

    // Connection state
    mqttConnected: false,
    deviceConnected: false,

    // UI state
    isManipulatingSlider: false,

    // Internal state
    client: null,
    updateTimer: null,
    hasReceivedInitialState: false,

    hasReceivedDevice1Solve: false,
    hasReceivedDevice2Solve: true,

    device1Finished: false,
    device2Finished: false,

    // ========================================================================
    // Computed Properties (Getters)
    // ========================================================================

    init(){
      this.connect();
    },

    get colorBoxColor() {
      return hsbToHex(this.hue * 360, this.saturation, 1.0);
    },

    get hueThumbColor() {
      return hsbToHex(this.hue * 360, 1.0, 1.0);
    },

    get hueThumbBorder() {
      return darkenHex(this.hueThumbColor, 20);
    },

    get saturationGradientEnd() {
      return hsbToHex(this.hue * 360, 1.0, 1.0);
    },

    get saturationThumbColor() {
      return hsbToHex(this.hue * 360, this.saturation, 1.0);
    },

    get saturationThumbBorder() {
      return darkenHex(this.saturationThumbColor, 20);
    },

    get brightnessThumbColor() {
      const gray = Math.round(this.brightness * 255);
      return `rgb(${gray}, ${gray}, ${gray})`;
    },

    get brightnessThumbBorder() {
      const gray = Math.max(0, Math.round(this.brightness * 255) - 50);
      return `rgb(${gray}, ${gray}, ${gray})`;
    },

    // ========================================================================
    // Lamp Control Methods
    // ========================================================================

    updateLamp() {
      if (!this.client || !this.mqttConnected) return;
      const config = {
        on: this.on,
        color: { h: this.hue, s: this.saturation },
        brightness: this.brightness,
        client: CLIENT_ID
      };
      this.client.publish(CONFIG.topics.setConfig, JSON.stringify(config), { qos: 1 });
    },

    //GOOD, REAL TOPIC!!!
    startGame() {
      console.log("statement ran!");
      if (!this.client || !this.mqttConnected) return;
      console.log("mqtt is connected!");
      this.client.publish("game1/started","started", { qos: 0});
      //this.client.publish("game1/started","started", { qos: 1});
      //this.client.publish("game1/lamp1/started","started", { qos: 0});

    },

    submitPuzzle() {
      if (!this.client || !this.mqttConnected) return;
      const payload = { h: this.hue, s: this.saturation, b: this.brightness };
      this.client.publish(CONFIG.topics.pubOnePuzzleState, JSON.stringify(payload), { qos: 1 });
    },

    sendWinStatement(){
      this.client.publish("game1/state", "win")
    },


    checkSolved(){
      if(this.hasReceivedDevice1Solve && this.hasReceivedDevice2Solve){
        this.sendWinStatement()
      }
    },

    // ========================================================================
    // MQTT Connection Methods
    // ========================================================================

    connect() {
      const brokerUrl = `ws://${HOST_ADDRESS}:${HOST_PORT}/`;

      this.client = mqtt.connect(brokerUrl, {
        clientId: CLIENT_ID,
        clean: true,
        reconnectPeriod: 1000,
        forceNativeWebSocket: true
      });

      this.client.on('connect', () => {
        console.log('Connected to MQTT broker');
        this.mqttConnected = true;

        this.client.subscribe(CONFIG.topics.lampChanged, (err) => {
          if (err) {
            console.error('Failed to subscribe to lamp changed:', err);
          }
        });

        this.client.subscribe(CONFIG.topics.lampServiceState, (err) => {
          if (err) {
            console.error('Failed to subscribe to lamp_service state:', err);
          }
        });

        this.client.subscribe(CONFIG.topics.lampUIState, (err) => {
          if (err) {
            console.error('Failed to subscribe to lamp_ui state:', err);
          }
        });

        this.client.subscribe("game/device_1/", (err) => {
          if (err) {
            console.error('Failed to subscribe to lamp_ui state:', err);
          }
        });

        this.client.subscribe("game1/state/explode", (err) => {
          if (err) {
            console.error('Failed to subscribe to lamp_ui state:', err);
          }
        });

      });

      this.client.on('message', (topic, payload) => {
        this.onMessageArrived(topic, payload.toString());
      });

      this.client.on('close', () => {
        console.log('Disconnected from MQTT broker');
        this.mqttConnected = false;
        this.deviceConnected = false;
      });

      this.client.on('error', (err) => {
        console.error('MQTT error:', err);
      });
    },

    // ======================================================================
    // Random Assorted Methods
    // ======================================================================

    timerTick() {
      const intervalId = setInterval(this.sendTimerMessage.bind(this), 1000);
    },

    stopTimer() {
      clearInterval(this.timerTick);
      
    },

    checkPartnerGameWon() {
      if(!this.hasReceivedDevice1Solve){
        return false;
      }
      if(!this.hasReceivedDevice2Solve){
        return false;
      }
      return true;
    },

    checkGameWon() {
      if(!this.device1Finished){
        return false;
      }
      if(!this.device2Finished){
        return false;
      }
      return true;
    },

    // ========================================================================
    // MQTT Message Handlers
    // ========================================================================

    onMessageArrived(topic, payloadString) {
      // Handle lamp connection state
      if (topic === CONFIG.topics.lampServiceState || topic === CONFIG.topics.lampUIState) {
        this.onConnectionStateMessage(payloadString);
        return;
      }

      //Handle when a state is published to Django
      if (topic === CONFIG.topics.receivingPuzzleState){ 
        this.onStateMessageArrived(payloadString);
        return;
       }

      if (topic === "game1/state/explode"){
        this.client.publish("game1/state/explosion", "exploded!!")
        window.location.href = "http://ec2-32-194-170-233.compute-1.amazonaws.com:8000/gameover";
        return;
      }

      if (topic === "game1/lamp1/submit"){
        this.hasReceivedDevice1Solve = true;
        if (!this.checkPartnerGameWon()){
          return;
        }
        this.client.publish("game1/lamp1/winGame")
        this.client.publish("game1/lamp2/winGame")
      }


      if (topic === "game1/lamp1/success"){
        this.device1Finished = true;
        if (!this.checkGameWon()){
          return;
        }
        window.location.href = "http://ec2-32-194-170-233.compute-1.amazonaws.com:8000/win.html/";
        return;
      }

      if (topic === "game1/lamp2/success"){
        this.device2Finished = true;
        if (!this.checkGameWon()){
          return;
        }
        window.location.href = "http://ec2-32-194-170-233.compute-1.amazonaws.com:8000/win.html/";
        return;
      }


      // Parse JSON for other messages
      let payload;
      try {
        payload = JSON.parse(payloadString);
      } catch (e) {
        console.error('Failed to parse MQTT message:', e);
        return;
      }

      if (topic === CONFIG.topics.lampChanged) {
        this.onLampStateMessage(payload);
      }
    },

    onLampStateMessage(payload) {
      // Receiving lamp/changed proves device is connected
      this.deviceConnected = true;

      if (payload.client === CLIENT_ID) {
        return;
      }

      if (this.isManipulatingSlider) {
        return;
      }

      // Payload contains color, brightness, on directly (no state wrapper)
      this.hue = payload.color.h;
      this.saturation = payload.color.s;
      this.brightness = payload.brightness;
      this.on = payload.on;
      this.hasReceivedInitialState = true;
    },

    //Takes: Array of states
    //Possible values: 'N', 'S', 'F', 'P
    onStateMessageArrived(payload){
      const states = payload.split(',');
      const stateCount = states.length;
      var solvedStates = 0;
      states.forEach(state => {
        if(state === 'N'){
          //implement Not Solved logic
          //...is there any Not Solved logic? it's published down there...
        }
        else if(state === 'S'){
          // implement Solved 
          solvedStates += 1;
        }
        else if(state === 'F'){
          // implement Failed Logic
          //this doesn't have to be exploded right away quite yet :)
          this.sendGameStateMessage('exploded');
        }
        else if(state === 'P'){
          // send all lampis state updated with P for 'in progress'
          this.sendAllStateChange('P');
          return;
        }

        //if there are an equal number of solved states and total states, win condition!
        if (solvedStates == stateCount){
          this.sendGameStateMessage('win');
        }

        //reflect state back to state topic (state ACK)
        this.sendOneStateChange(payload);
        
        
      });
    },

    onConnectionStateMessage(payloadString) {
      // lamp/connection/+/state topic returns "1" (connected) or "0" (disconnected)
      this.deviceConnected = payloadString === "1";
    },

    // ========================================================================
    // UI Event Handlers
    // ========================================================================

    onSliderInput(slider, value) {
      this.scheduleConfigChange();
      mixpanel.track('Slider Change', {
        'event_type': 'ui',
        'slider': slider,
        'value': value
      });
    },

    togglePower() {
      this.on = !this.on;
      this.sendConfigChange();
      mixpanel.track('Toggle Power', {
        'event_type': 'ui',
        'isOn': this.on
      });
    },

    // ========================================================================
    // MQTT Publishing Methods
    // ========================================================================

    //publish a message on timer topic (implemented every second on the actual python)
    //process timer logic on kivy?
    sendTimerMessage() {
      if (!this.client || !this.mqttConnected) {
        return;
      }
      
      this.client.publish(CONFIG.topics.timer,new Date().toISOString());
    },

    //sends state of game to the lampis (started, exploded, paused, win)
    sendGameStateMessage(state) {
      if (!this.client || !this.mqttConnected) {
        return;
      }
      this.client.publish(CONFIG.topics.gameState, state);
    },

    sendAllStateChange(state) {
      if (!this.client || !this.mqttConnected) {
        return;
      }

      this.client.publish(CONFIG.topics.pubAllPuzzleState, state);
    },

    
    sendOneStateChange(state) {
      if (!this.client || !this.mqttConnected) {
        return;
      }

      this.client.publish(CONFIG.topics.pubOnePuzzleState, state);
    },

    scheduleConfigChange() {
      if (this.updateTimer !== null) {
        clearTimeout(this.updateTimer);
      }
      this.updateTimer = setTimeout(() => {
        this.updateTimer = null;
        this.sendConfigChange();
      }, 100);
    },

    sendConfigChange() {
      if (!this.client || !this.mqttConnected) {
        return;
      }

      const config = {
        client: CLIENT_ID,
        color: {
          h: this.hue,
          s: this.saturation
        },
        brightness: this.brightness,
        on: this.on
      };

      this.client.publish(CONFIG.topics.setConfig, JSON.stringify(config));
    }
  };
}

// Make the component available to Alpine.js
window.lampController = lampController;
