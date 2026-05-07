/**
 * LAMPI Web Controller
 *
 * This module implements the Alpine.js component that controls the LAMPI
 * smart lamp through MQTT over WebSockets.
 */

import mqtt from 'mqtt';
import { hsbToHex, darkenHex } from './color-utils.js';

// ============================================================================
// Configuration Constants
// ============================================================================

// Broker connection settings
const HOST_ADDRESS = window.location.hostname;  // EC2 hostname (same as web server)
const HOST_PORT = 50002;                         // WebSocket port (NOT the MQTT port!)

// Generate a unique client ID to identify this browser session
// MQTT requires each client to have a unique ID
const CLIENT_ID = Math.random().toString(36).substring(2) + '_web_client';

// Device ID and session key from Django template (LAMPI_CONFIG)
// Chapter 14 uses device_id as MQTT username and session_key as password
// for WebSocket authentication via the mosquitto-go-auth plugin
const DEVICE_ID = (window.LAMPI_CONFIG || {}).deviceId || '';
const SESSION_KEY = (window.LAMPI_CONFIG || {}).sessionKey || '';

// MQTT topic patterns - these are the CLOUD broker topics (after bridge remapping)
// The LAMPI uses simple topics locally (lamp/changed, lamp/set_config)
// The bridge remaps these to devices/{device_id}/lamp/... on the cloud broker
const TOPIC_SET_CONFIG = `devices/${DEVICE_ID}/lamp/set_config`;
const TOPIC_LAMP_CHANGED = `devices/${DEVICE_ID}/lamp/changed`;

// LAMPI broker bridge connection state - indicates if the device's bridge is online
// Mosquitto publishes "1" when the bridge connects and "0" when it disconnects
const TOPIC_CONNECTION_STATE = `$SYS/broker/connection/${DEVICE_ID}_broker/state`;

// ============================================================================
// Alpine.js Component Definition
// ============================================================================

/**
 * Creates the lamp controller Alpine.js component
 *
 * This function returns an object that Alpine.js uses to:
 * - Track reactive state (hue, saturation, brightness, on)
 * - Compute derived values (colors for UI elements)
 * - Handle user interactions (slider changes, power button)
 * - Manage MQTT communication
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
    isManipulatingSlider: false,  // True while user is dragging a slider

    // Internal state (not displayed)
    client: null,                  // MQTT client instance
    updateTimer: null,             // Debounce timer for sending updates
    hasReceivedInitialState: false,

    // ========================================================================
    // Computed Properties (Getters)
    // ========================================================================

    // These are recalculated whenever their dependencies change

    /** Color for the preview box (shows current hue/saturation at full brightness) */
    get colorBoxColor() {
      return hsbToHex(this.hue * 360, this.saturation, 1.0);
    },

    /** Hue slider thumb color (pure hue at full saturation/brightness) */
    get hueThumbColor() {
      return hsbToHex(this.hue * 360, 1.0, 1.0);
    },

    /** Hue slider thumb border (darkened version of thumb color) */
    get hueThumbBorder() {
      return darkenHex(this.hueThumbColor, 20);
    },

    /** Saturation slider gradient end color (current hue at full saturation) */
    get saturationGradientEnd() {
      return hsbToHex(this.hue * 360, 1.0, 1.0);
    },

    /** Saturation slider thumb color */
    get saturationThumbColor() {
      return hsbToHex(this.hue * 360, this.saturation, 1.0);
    },

    /** Saturation slider thumb border */
    get saturationThumbBorder() {
      return darkenHex(this.saturationThumbColor, 20);
    },

    /** Brightness slider thumb color (grayscale based on brightness) */
    get brightnessThumbColor() {
      const gray = Math.round(this.brightness * 255);
      return `rgb(${gray}, ${gray}, ${gray})`;
    },

    /** Brightness slider thumb border */
    get brightnessThumbBorder() {
      const gray = Math.max(0, Math.round(this.brightness * 255) - 50);
      return `rgb(${gray}, ${gray}, ${gray})`;
    },

    // ========================================================================
    // MQTT Connection Methods
    // ========================================================================

    /**
     * Connect to the MQTT broker via WebSockets
     */
    connect() {
      // Build the WebSocket URL
      const brokerUrl = `wss://${HOST_ADDRESS}:${HOST_PORT}/`;

      // Connect to the broker with options
      this.client = mqtt.connect(brokerUrl, {
        clientId: CLIENT_ID,
        username: DEVICE_ID,
        password: SESSION_KEY,
        clean: true,
        reconnectPeriod: 1000
      });

      // Handle successful connection
      this.client.on('connect', () => {
        console.log('Connected to MQTT broker');
        this.mqttConnected = true;

        // Subscribe to lamp state changes
        this.client.subscribe(TOPIC_LAMP_CHANGED, (err) => {
          if (err) {
            console.error('Failed to subscribe to lamp changed:', err);
          }
        });

        // Subscribe to LAMPI service connection state
        this.client.subscribe(TOPIC_CONNECTION_STATE, (err) => {
          if (err) {
            console.error('Failed to subscribe to connection state:', err);
          }
        });
      });

      // Handle incoming messages
      this.client.on('message', (topic, payload) => {
        this.onMessageArrived(topic, payload.toString());
      });

      // Handle connection close
      this.client.on('close', () => {
        console.log('Disconnected from MQTT broker');
        this.mqttConnected = false;
        this.deviceConnected = false;
      });

      // Handle errors
      this.client.on('error', (err) => {
        console.error('MQTT error:', err);
      });
    },

    // ========================================================================
    // MQTT Message Handlers
    // ========================================================================

    /**
     * Handle incoming MQTT messages
     *
     * @param {string} topic - The MQTT topic the message was received on
     * @param {string} payloadString - The message payload as a string
     */
    onMessageArrived(topic, payloadString) {
      // Route message to appropriate handler based on topic
      if (topic === TOPIC_LAMP_CHANGED) {
        // Lamp state messages are JSON
        try {
          const payload = JSON.parse(payloadString);
          this.onLampStateMessage(payload);
        } catch (e) {
          console.error('Failed to parse lamp state message:', e);
        }
      } else if (topic === TOPIC_CONNECTION_STATE) {
        // Connection state is just "1" or "0", not JSON
        this.onConnectionStateMessage(payloadString);
      }
    },

    /**
     * Handle lamp state change messages
     *
     * This method updates the UI to reflect the lamp's current state,
     * but ONLY if:
     * - The user is not currently manipulating a slider
     * - The message wasn't sent by this client (prevents feedback loops)
     *
     * @param {Object} payload - Parsed message payload with color, brightness, on, client
     */
    onLampStateMessage(payload) {
      // Ignore our own messages (prevents feedback loops)
      if (payload.client === CLIENT_ID) {
        return;
      }

      // Don't update while user is dragging sliders (prevents jumping)
      if (this.isManipulatingSlider) {
        return;
      }

      // Update our state from the received values
      this.hue = payload.color.h;
      this.saturation = payload.color.s;
      this.brightness = payload.brightness;
      this.on = payload.on;
      this.hasReceivedInitialState = true;
    },

    /**
     * Handle LAMPI service connection state messages
     *
     * Updates deviceConnected based on lamp service status.
     * The lamp_service.py uses LWT to publish "1" when connected, "0" when disconnected.
     *
     * @param {string} payload - The raw payload ("1" or "0")
     */
    onConnectionStateMessage(payload) {
      this.deviceConnected = payload === '1';
    },

    // ========================================================================
    // UI Event Handlers
    // ========================================================================

    /**
     * Called when any slider value changes
     *
     * Schedules a debounced config change to avoid flooding the broker
     */
    onSliderInput() {
      this.scheduleConfigChange();
    },

    /**
     * Toggle the lamp power state
     */
    togglePower() {
      this.on = !this.on;
      this.sendConfigChange();
    },

    // ========================================================================
    // MQTT Publishing Methods
    // ========================================================================

    /**
     * Schedule a config change with debouncing
     *
     * This prevents sending too many messages while the user drags sliders
     */
    scheduleConfigChange() {
      if (this.updateTimer !== null) {
        clearTimeout(this.updateTimer);
      }
      this.updateTimer = setTimeout(() => {
        this.updateTimer = null;
        this.sendConfigChange();
      }, 100);  // 100ms debounce delay
    },

    /**
     * Send the current lamp configuration to the broker
     */
    sendConfigChange() {
      if (!this.client || !this.mqttConnected) {
        return;
      }

      // Build the config object matching the lamp's expected format
      const config = {
        client: CLIENT_ID,
        color: {
          h: this.hue,
          s: this.saturation
        },
        brightness: this.brightness,
        on: this.on
      };

      // Publish to the set_config topic
      this.client.publish(TOPIC_SET_CONFIG, JSON.stringify(config));
    }
  };
}

// ============================================================================
// Export to Global Scope
// ============================================================================

// Make the component available to Alpine.js
// Alpine looks for this function in the global scope when it sees x-data="lampController()"
window.lampController = lampController;
