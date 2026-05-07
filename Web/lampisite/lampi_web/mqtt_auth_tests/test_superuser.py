#! /usr/bin/env python3

import unittest
import requests
from test_common import *


# /superuser
class TestSuperuser(unittest.TestCase):

    def test_superuser_not_allowed(self):
        r = requests.post(SUPERUSER_URL)
        self.assertEqual(r.status_code, HTTP_FORBIDDEN)


if __name__ == "__main__":
    unittest.main(verbosity=1,
                  failfast=True)
