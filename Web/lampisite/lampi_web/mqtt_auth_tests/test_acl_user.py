#! /usr/bin/env python3

import unittest
import requests
from test_common import *

# Remember ACL is only checked *after* a user has been authenticated

# authenticated users (Django superusers, like mqtt-daemon,
#  and websockets MQTT) should be able to interact with these
#  TOPICS where the "{}" is replaced with a specific deviceid
#
# for READ
USER_READ_TOPIC_LIST = [
  "$SYS/broker/connection/{}_broker/state",
  "devices/{}/lamp/connection/lamp_service/state",
  "devices/{}/lamp/connection/lamp_ui/state",
  "devices/{}/lamp/connection/lamp_bt_peripheral/state",
  "devices/{}/lamp/connection/bluetooth/state",
  "devices/{}/lamp/changed",
]
# for WRITE
USER_WRITE_TOPIC_LIST = [
  "devices/{}/lamp/set_config",
]


class TestACLforUsers(unittest.TestCase):

    def test_acl_fail_on_GET(self):
        # ACL should return 403 on any HTTP verb other than POST
        r = requests.get(ACL_URL)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_acl_mqtt_daemon_approved_for_arbitrary_topic(self):
        data = {
                "username": MQTT_DAEMON_USERNAME,
                "password": "",  # ignored for ACL
                "topic": "ello",  # an arbitrary topic
                "acc": ACL_READ,
                "clientid": ""
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_acl_device_websocket_cannot_write_TOPIC_changed(self):
        data = {
                "username": DEVICE_ID,
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/changed".format(DEVICE_ID),
                "acc": ACL_WRITE,
                "clientid": ""
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_acl_device_websocket_can_read_TOPIC_changed(self):
        data = {
                "username": DEVICE_ID,
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/changed".format(DEVICE_ID),
                "acc": ACL_READ,
                "clientid": ""
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_acl_device_websocket_can_write_TOPIC_set_config(self):
        data = {
                "username": DEVICE_ID,
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/set_config".format(DEVICE_ID),
                "acc": ACL_WRITE,
                "clientid": ""
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_acl_device_websocket_cannot_read_TOPIC_set_config(self):
        data = {
                "username": DEVICE_ID,
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/set_config".format(DEVICE_ID),
                "acc": ACL_READ,
                "clientid": ""
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)


if __name__ == "__main__":
    unittest.main(verbosity=1,
                  failfast=True)
