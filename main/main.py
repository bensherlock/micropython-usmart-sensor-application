#! /usr/bin/env python
#
# MicroPython USMART Sensor Application
#
# This file is part of micropython-usmart-sensor-application.
# https://github.com/bensherlock/micropython-usmart-sensor-application
#
#
# MIT License
#
# Copyright (c) 2020 Benjamin Sherlock <benjamin.sherlock@ncl.ac.uk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""MicroPython USMART Sensor Application."""

# import network
import json
import os
import pyb
import machine
import utime
from ota_updater.main.ota_updater import OTAUpdater
import jotter

# Add your own ota updateable application modules to this list.
ota_modules = ['mainloop,', 'ota_updater', 'pybd_expansion', 'sensor_payload', 'uac_localisation', 'uac_modem',
               'uac_network']


def load_wifi_config():
    """Load Wifi Configuration from JSON file."""
    wifi_config = None
    config_filename = 'config/wifi_cfg.json'
    try:
        with open(config_filename) as json_config_file:
            wifi_config = json.load(json_config_file)
    except Exception:
        pass

    return wifi_config


def load_ota_config(module_name):
    """Load OTA Configuration from JSON file."""
    ota_config = None
    config_filename = 'config/' + module_name + '_gitrepo_cfg.json'
    try:
        with open(config_filename) as json_config_file:
            ota_config = json.load(json_config_file)
    except Exception:
        pass

    return ota_config


def download_and_install_updates_if_available():
    # Wifi Configuration
    wifi_cfg = load_wifi_config()
    if not wifi_cfg:
        # No wifi configuration
        print('No wifi config info')
        return False

    # Open Wifi
    if not OTAUpdater.using_network(wifi_cfg['wifi']['ssid'], wifi_cfg['wifi']['password']):
        # Failed to connect
        print("Unable to connect to wifi")
        return False

    # Startup Load Configuration For Each Module and check for updates, download if available, then overwrite main/
    for ota_module in ota_modules:
        print("ota_module=" + ota_module)
        ota_cfg = load_ota_config(ota_module)
        if ota_cfg:
            o = OTAUpdater(ota_cfg['gitrepo']['url'], ota_module)
            # download_updates_if_available - Checks version numbers and downloads into next/
            o.download_updates_if_available()
            # apply_pending_updates_if_available - Moves next/ into main/
            o.apply_pending_updates_if_available()

            # Now need to reboot to make use of the updated modules
    machine.reset()


def boot():
    # Check reason for reset - only update if power on reset
    # if machine.reset_cause() == machine.PWRON_RESET:
    #    download_and_install_updates_if_available()  # commented out during development

    # Start the main application
    start()


def start():
    # Run the application from the MainLoop.
    # jotter.get_jotter().jot("start()", source_file=__name__)

    # Red and Green LEDs on during the startup wait period
    pyb.LED(1).on()
    pyb.LED(2).on()

    # Debug Modes
    # https://forum.micropython.org/viewtopic.php?t=6222
    # Check if USB cable is plugged in to a PC. If so, then we may want to wait a period before launching the program.
    # If you want to detect if the USB is plugged in to a PC and enumerated, but may or may not have a serial terminal
    # connection, then inspect the registers directly:
    usb_cable_connected = False
    USB_HS = 0x40040000
    USB_FS = 0x50000000
    if machine.mem32[USB_HS] & (1 << 19):  # check BSVLD bit
        # have USB HS connection
        usb_cable_connected = True
    if machine.mem32[USB_FS] & (1 << 19):  # check BSVLD bit
        # have USB FS connection
        usb_cable_connected = True

    # The above seems to happen even if the USB cable isn't connected to a PC?

    timeout_start = utime.time()
    if usb_cable_connected:
        while utime.time() < timeout_start + 30:
            utime.sleep_ms(100)

    # Red and Green LEDs off after the startup wait period
    pyb.LED(1).off()
    pyb.LED(2).off()

    # Now run the mainloop
    try:
        import mainloop.main.mainloop as ml
        jotter.get_jotter().jot("start()::run_mainloop()", source_file=__name__)
        ml.run_mainloop()
    except Exception as the_exception:
        jotter.get_jotter().jot_exception(the_exception)

        import sys
        sys.print_exception(the_exception)
        pass
        # Log to file

    pass


# Run boot()
boot()
