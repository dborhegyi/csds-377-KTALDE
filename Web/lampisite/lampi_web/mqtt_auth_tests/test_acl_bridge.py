#! /usr/bin/env python3

import unittest
import requests
from test_common import *

# Remember ACL is only checked *after* a user has been authenticated

# authenticated bridges
#  should be able to interact with these TOPICS
#  where the "{}" is replaced with a specific deviceid
# for READ
DEVICE_BRIDGE_READ_TOPIC_LIST = [
  "devices/{}/lamp/set_config",
  "devices/{}/lamp/associated",
]
# for WRITE
DEVICE_BRIDGE_WRITE_TOPIC_LIST = [
  "$SYS/broker/connection/{}_broker/state",
  "devices/{}/lamp/connection/lamp_service/state",
  "devices/{}/lamp/connection/lamp_ui/state",
  "devices/{}/lamp/connection/lamp_bt_peripheral/state",
  "devices/{}/lamp/connection/bluetooth/state",
  "devices/{}/lamp/changed",
]


class TestACLforBridges(unittest.TestCase):

    def test_acl_bridge_can_read_TOPIC_set_config(self):
        # note: clientid must match username for bridges
        data = {
                "username": DEVICE_ID + "_broker",
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/set_config".format(DEVICE_ID),
                "acc": ACL_READ,
                "clientid": DEVICE_ID + "_broker"
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_acl_bridge_cannot_write_TOPIC_set_config(self):
        # note: clientid must match username for bridges
        data = {
                "username": DEVICE_ID + "_broker",
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/set_config".format(DEVICE_ID),
                "acc": ACL_WRITE,
                "clientid": DEVICE_ID + "_broker"
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_acl_bridge_can_read_TOPIC_associated(self):
        # note: clientid must match username for bridges
        data = {
                "username": DEVICE_ID + "_broker",
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/associated".format(DEVICE_ID),
                "acc": ACL_READ,
                "clientid": DEVICE_ID + "_broker"
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_acl_bridge_cannot_write_TOPIC_associated(self):
        # note: clientid must match username for bridges
        data = {
                "username": DEVICE_ID + "_broker",
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/associated".format(DEVICE_ID),
                "acc": ACL_WRITE,
                "clientid": DEVICE_ID + "_broker"
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_acl_bridge_can_write_TOPIC_changed(self):
        # note: clientid must match username for bridges
        data = {
                "username": DEVICE_ID + "_broker",
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/changed".format(DEVICE_ID),
                "acc": ACL_WRITE,
                "clientid": DEVICE_ID + "_broker"
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_acl_bridge_cannot_read_TOPIC_changed(self):
        # note: clientid must match username for bridges
        data = {
                "username": DEVICE_ID + "_broker",
                "password": "",  # ignored for ACL
                "topic": "devices/{}/lamp/changed".format(DEVICE_ID),
                "acc": ACL_READ,
                "clientid": DEVICE_ID + "_broker"
               }
        r = requests.post(ACL_URL, data=data)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)


if __name__ == "__main__":
    unittest.main(verbosity=1,
                  failfast=True)
