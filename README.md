# NasServerFanController

This code will allow you to automatize the fan speed control using a Raspberry PI.

## Instructions

1. Clone this repository in the Rasbperry PI and throught the terminal access the directory
2. Run this command to install the libraries: `pip3 install -r requirements.txt`
3. Start the pigpio daemon by running `sudo pigpiod`
4. Run the `main.py` file using `python3 main.py`

## Open Media Vault

The script can be run at startup by adding it in the scheduled jobs through the control panel of OMV
