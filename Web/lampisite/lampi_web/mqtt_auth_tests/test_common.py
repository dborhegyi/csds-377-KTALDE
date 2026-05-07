# UPDATE THE FOLLOWING TO MATCH YOUR SYSTEM
#
# your EC2 hostname
EC2_HOSTNAME = "ec2-52-4-233-176.compute-1.amazonaws.com"
# a device ID for a LAMPI configured on your system
DEVICE_ID = "b827eb8f3d71"
# the Django user that the LAMPI device is associated with
DEVICE_USER = "admin"
# the Django user password
DEVICE_USER_PASSWORD = "iot12345"

# Base URL possible including a ":" and port number
BASEURL = "http://127.0.0.1:8080"

#
# DO NOT MODIFY BELOW THIS LINE
#

# disable TLS warnings
# see https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings

import urllib3  # nopep8

urllib3.disable_warnings()

# These are the three URLs suppored by mqtt_auth_views
GETUSER_URL = BASEURL + "/lampi/auth"
SUPERUSER_URL = BASEURL + "/lampi/superuser"
ACL_URL = BASEURL + "/lampi/acl"

MQTT_DAEMON_USERNAME = "mqtt-daemon"

# Our Django code for mqtt_auth_views should only return
#  one of these HTTP Status Codes
HTTP_SUCCESS = 200
HTTP_FORBIDDEN = 403

# auth plugin ACL values
ACL_READ = "1"
ACL_WRITE = "2"
ACL_SUBSCRIBE = "4"
