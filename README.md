# micropython-usmart-sensor-application
USMART Sensor Node Application

Top level application for the sensor nodes using PYBD and the expansion PCB. 

Everything below this level, modules and the mainloop can be updated OTA in the field. 

 
## Usage

Copy the contents of main/ to the root directory of the PYBD USB MSD.

Create a wifi_cfg.json file using the template as an example and populate with appropriate SSID and PASSWORD values. Note that .gitignore is set to ignore this config file in this repository.

On POR (Power On Reset) the program will attempt to connect to the wifi and then check GitHub for the latest release versions of the modules (ota_updater etc) and then download them before rebooting the device. After running you should now see these modules updated.

For information on the OTA Updater including how to use it in an example application  see [github.com/bensherlock/micropython-ota-updater](https://github.com/bensherlock/micropython-ota-updater).

## Modules

This application will OTA update modules from the following repositories:
+ ota_updater: [micropython-ota-updater](https://github.com/bensherlock/micropython-ota-updater)
+ mainloop: [micropython-usmart-sensor-mainloop](https://github.com/bensherlock/micropython-usmart-sensor-mainloop)
+ pybd_expansion: [micropython-pybd-expansion](https://github.com/bensherlock/micropython-pybd-expansion)
+ uac_modem: [micropython-unm3-pybd](https://github.com/bensherlock/micropython-unm3-pybd)
+ uac_network: [micropython-usmart-network](https://github.com/bensherlock/micropython-usmart-network)
+ uac_localisation: [micropython-usmart-localisation](https://github.com/bensherlock/micropython-usmart-localisation)
+ sleep:
