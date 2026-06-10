import time

import actions.computer_settings as cs

# Basic smoke tests for WPCTL and brightnessctl

def test_volume_up_and_down():
    # Increase volume
    cs.volume_up()
    time.sleep(0.5)
    # Decrease volume
    cs.volume_down()
    time.sleep(0.5)


def test_brightness_up_and_down():
    # Increase brightness
    cs.brightness_up()
    time.sleep(0.5)
    # Decrease brightness
    cs.brightness_down()
    time.sleep(0.5)
