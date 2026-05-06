#! /usr/bin/env python3

from test_superuser import *
from test_getuser import *
from test_acl_user import *
from test_acl_bridge import *


if __name__ == "__main__":
    unittest.main(verbosity=1,
                  failfast=True)
