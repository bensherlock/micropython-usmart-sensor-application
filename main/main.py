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
ota_modules = ['mainloop', 'ota_updater', 'pybd_expansion', 'sensor_payload', 'uac_localisation', 'uac_modem',
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


def get_installed_module_versions():
    """Get the version of each of the installed modules.
    Returns a dictionary of module to version pairs"""
    mod_version_dictionary = {}

    try:
        # Startup Load Configuration For Each Module and get version
        for ota_module in ota_modules:
            if ota_module:
                print("ota_module=" + ota_module)
                ota_cfg = load_ota_config(ota_module)
                if ota_cfg:
                    o = OTAUpdater(ota_cfg['gitrepo']['url'], ota_module)
                    v = o.get_current_version()
                    mod_version_dictionary[ota_module] = v

        pass
    except Exception:
        pass

    return mod_version_dictionary


def download_and_install_updates_if_available():
    """Connects to WiFi and checks for all modules for updates. This function will always cause a machine reset. """
    try:
        # Need to start the WDT during this. And to finish with the reset.
        import machine
        # Firstly Initialise the Watchdog machine.WDT. This cannot now be stopped and *must* be fed.
        wdt = machine.WDT(timeout=30000)  # 30 seconds timeout on the watchdog.

        # Feed the watchdog
        wdt.feed()

        # Wifi Configuration
        wifi_cfg = load_wifi_config()
        if not wifi_cfg:
            # No wifi configuration
            print('No wifi config info')
            raise Exception("No wifi config info")

        # Feed the watchdog
        wdt.feed()

        import network
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(False) # disable wifi if currently active - in case of issues from a previous run
        sta_if.deinit()
        #sta_if.config(trace=1)

        utime.sleep_ms(1000) # yield and wait for supply to stabilise

        # Feed the watchdog
        wdt.feed()

        # Open Wifi
        if not OTAUpdater.using_network(wifi_cfg['wifi']['ssid'], wifi_cfg['wifi']['password']):
            # Failed to connect
            print("Unable to connect to wifi")
            raise Exception("Unable to connect to wifi")

        # Feed the watchdog
        wdt.feed()

        # Startup Load Configuration For Each Module and check for updates, download if available, then overwrite main/
        for ota_module in ota_modules:
            # Feed the watchdog
            wdt.feed()

            print("ota_module=" + ota_module)
            ota_cfg = load_ota_config(ota_module)
            if ota_cfg:
                github_pat = None
                if wifi_cfg.get('github') and wifi_cfg['github'].get('pat'):
                    github_pat = wifi_cfg['github']['pat']

                o = OTAUpdater(ota_cfg['gitrepo']['url'], ota_module, github_pat=github_pat)
                # download_updates_if_available - Checks version numbers and downloads into next/
                o.download_updates_if_available()
                # apply_pending_updates_if_available - Moves next/ into main/
                o.apply_pending_updates_if_available()

    except Exception as the_exception:
        import sys
        sys.print_exception(the_exception)
        pass

    finally:
        utime.sleep_ms(2000) # pause to let print statements complete
        # Now need to reboot to make use of the updated modules
        machine.reset()


def low_power_pins(disable_3v3=False, disable_leds=False):
    # from https://github.com/micropython/micropython/issues/4686
    pins = [
        # user IO pins
        'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15',
        'B0', 'B1', 'B3', 'B4', 'B5', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13',
        'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
        'D0', 'D3', 'D8', 'D9',
        'E0', 'E1', 'E12', 'E14', 'E15',
        'F1', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F13', 'F14', 'F15',
        'H2', 'H3', 'H5', 'H6', 'H7', 'H8',
        'I0', 'I1',

        # internal pins
        'D1', 'D14', 'D15',
        'F0', 'F12',
        'G0', 'G1', 'G2', 'G3', 'G4', 'G5', #'G6',
        'H4', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15',
        'I2', 'I3',
    ]
    pins_led = ['F3', 'F4', 'F5',]
    pins_sdmmc = ['D6', 'D7', 'G9', 'G10', 'G11', 'G12']
    pins_wlan = ['D2', 'D4', 'I7', 'I8', 'I9', 'I11']
    pins_bt = ['D5', 'D10', 'E3', 'E4', 'E5', 'E6', 'G8', 'G13', 'G14', 'G15', 'I4', 'I5', 'I6', 'I10']
    pins_qspi1 = ['B2', 'B6', 'D11', 'D12', 'D13', 'E2']
    pins_qspi2 = ['E7', 'E8', 'E9', 'E10', 'E11', 'E13']
    for p in pins:
        pyb.Pin(p, pyb.Pin.IN, pyb.Pin.PULL_DOWN)
    if disable_3v3:
       pyb.Pin('EN_3V3', pyb.Pin.IN, None)
    if disable_leds:
        for p in pins_led:
            pyb.Pin(p, pyb.Pin.IN, pyb.Pin.PULL_UP)

def boot():
    # Check battery voltage and if below a set value power off all peripherals and permanently enter deepsleep.
    # Letting the battery run down and repeat brownout/POR damages the PYBD.

    # Cycle the NM3 power supply on the powermodule
    try:
        import pyb
        import machine
        from pybd_expansion.main.powermodule import PowerModule
        powermodule = PowerModule()


        # 2 second delay at the start to allow battery voltage at the ADC to stabilise.
        timeout_start = utime.time()
        while utime.time() < timeout_start + 2:
            utime.sleep_ms(100)


        vbatt_volts = powermodule.get_vbatt_reading()

        if vbatt_volts < 3.6:
            # Turn off the USB
            pyb.usb_mode(None)

            low_power_pins(disable_3v3=True, disable_leds=True)

            powermodule.disable_nm3() # Needs to be driven low in order to pull-down the external resistor.

            while 1:
                machine.lightsleep() # Enter lightsleep
                utime.sleep_ms(100)


    except Exception as the_exception:
        import sys
        sys.print_exception(the_exception)
        pass


    # Check reason for reset - only update if power on reset.
    #try:
    #    if machine.reset_cause() == machine.PWRON_RESET:
    #        download_and_install_updates_if_available()  # commented out during development
    #except Exception as the_exception:
    #    jotter.get_jotter().jot_exception(the_exception)
    #    import sys
    #    sys.print_exception(the_exception)
    #    pass
    #    # Log to file

    # 2021-09-02
    # The update on POR has been disabled for now. Low-battery brownouts on long-term deployed units may well have
    # resulted in many many POR update events. As the MicroPython firmware pushes new driver firmware to the wifi SoC
    # everytime active(True) is called (on powerup of the wifi SoC) this may have detrimental effect.
    # See open issue: https://github.com/micropython/micropython/issues/7738

    # Manual OTA request
    try:
        # Check for the flag file .USOTA
        if '.USOTA' in os.listdir():
            # Then update is required
            # Remove the file first
            os.remove('.USOTA')
            download_and_install_updates_if_available()

    except Exception as the_exception:
        jotter.get_jotter().jot_exception(the_exception)

        import sys
        sys.print_exception(the_exception)
        pass
        # Log to file

    # Start the main application
    # try:
    start()
    # except
    # If it's a keyboard interrupt then we've connected via REPL so don't restart.
    # If we return from start() then things have crashed so reset the device.
    #    machine.reset()


def start():
    # Run the application from the MainLoop.
    try:
        # jotter.get_jotter().jot("start()", source_file=__name__)
        # Red and Green LEDs on during the startup wait period
        pyb.LED(1).on()
        pyb.LED(2).on()

        # 30 second delay at the start to connect via REPL and kill the program before it fires up the WDT.
        timeout_start = utime.time()
        while utime.time() < timeout_start + 30:
            utime.sleep_ms(100)

        # Red and Green LEDs off after the startup wait period
        pyb.LED(1).off()
        pyb.LED(2).off()

    except Exception as the_exception:
        jotter.get_jotter().jot_exception(the_exception)

        import sys
        sys.print_exception(the_exception)
        pass
        # Log to file

    # Get installed modules and versions
    installed_modules = None
    try:
        installed_modules = get_installed_module_versions()
        if installed_modules:
            print("Installed Modules")
            for (mod, version) in installed_modules.items():
                print(str(mod) + " : " + str(version))
    except Exception as the_exception:
        jotter.get_jotter().jot_exception(the_exception)

        import sys
        sys.print_exception(the_exception)
        pass
        # Log to file

    # Now run the mainloop
    try:
        import mainloop.main.mainloop as ml
        env_variables = {"installedModules": installed_modules}
        ml.set_environment_variables(env_variables)
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
