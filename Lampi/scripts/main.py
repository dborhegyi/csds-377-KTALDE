#!/usr/bin/env python3
# previously frmo chapter 8
#from lampi_touch.lampi_app import LampiApp

#if __name__ == "__main__":
#    LampiApp().run()

# chapter 2's implementation
#!/usr/bin/env python3
import os
from lampi_touch.lampi_app import LampiApp
from kivy.config import Config

if __name__ == "__main__":
        touch_device = os.environ.get('TOUCH_DEVICE')
        if touch_device:
                Config.set('input',
                           'pitft',
                           'mtdev,{dev},rotation=90,invert_x=1,max_position_x=240,max_position_y=320'.format(dev=touch_device)
                           )
        LampiApp().run()
