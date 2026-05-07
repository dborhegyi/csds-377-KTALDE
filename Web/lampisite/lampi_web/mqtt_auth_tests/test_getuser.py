#! /usr/bin/env python3

import unittest
import requests
from test_common import *


# /auth
class TestDjangoUsers(unittest.TestCase):
    def test_user_not_authenticated_without_username(self):
        r = requests.post(GETUSER_URL, data={
                                             "username": ""
                                            }
                          )
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_mqtt_daemon_user_not_authenticated_without_password(self):
        r = requests.post(GETUSER_URL, data={
                                             "username": MQTT_DAEMON_USERNAME
                                            }
                          )
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_mqtt_daemon_user_not_authenticated_with_wrong_password(self):
        r = requests.post(GETUSER_URL, data={
                                             "username": MQTT_DAEMON_USERNAME,
                                             "password": "wrong",
                                            }
                          )
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)

    def test_mqtt_daemon_user_authenticated_with_password(self):
        r = requests.post(GETUSER_URL, data={
                                             "username": MQTT_DAEMON_USERNAME,
                                             "password": "eecs397-iot",
                                            }
                          )
        self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_admin_user_authenticated_with_password(self):
        r = requests.post(GETUSER_URL, data={
                                             "username": "admin",
                                             "password": "iot12345",
                                            }
                          )
        self.assertEqual(r.status_code, HTTP_SUCCESS)


class TestDjangoUserWebSockets(unittest.TestCase):

    def test_admin_user_auth_websockets(self):
        url = "https://" + EC2_HOSTNAME + "/login/?next=/"
        # establish an authenticated HTTPS connection to Django
        with requests.Session() as s:

            get_resp = s.get(url, verify=False)
            post_data = {
                "csrfmiddlewaretoken": s.cookies["csrftoken"],
                "username": DEVICE_USER,
                "password": DEVICE_USER_PASSWORD,
                }

            headers = {"Origin": "https://" + EC2_HOSTNAME}
            login_resp = s.post(url, data=post_data, headers=headers,
                                verify=False)
            self.assertEqual(login_resp.status_code, HTTP_SUCCESS)
            # with authenticated HTTPS session, test websockets
            #  the cookie sessionid is the password for this use case
            data = {
                    "username": DEVICE_ID,
                    "password": s.cookies["sessionid"]
                    }
            r = requests.post(GETUSER_URL, data=data)
            self.assertEqual(r.status_code, HTTP_SUCCESS)

    def test_admin_user_no_auth_websockets(self):
        url = "https://" + EC2_HOSTNAME + "/login/?next=/"
        # establish an authenticated HTTPS connection to Django
        with requests.Session() as s:

            get_resp = s.get(url, verify=False)
            post_data = {
                "csrfmiddlewaretoken": s.cookies["csrftoken"],
                "username": DEVICE_USER,
                "password": DEVICE_USER_PASSWORD,
                }

            headers = {"Origin": "https://" + EC2_HOSTNAME}
            login_resp = s.post(url, data=post_data, headers=headers,
                                verify=False)
            self.assertEqual(login_resp.status_code, HTTP_SUCCESS)
            # with authenticated HTTPS session, test websockets
            #  pass an INVALID value as the password
            data = {
                    "username": DEVICE_ID,
                    "password": "9876543210"
                    }
            r = requests.post(GETUSER_URL, data=data)
            self.assertEqual(r.status_code, HTTP_FORBIDDEN)


if __name__ == "__main__":
    unittest.main(verbosity=1,
                  failfast=True)
