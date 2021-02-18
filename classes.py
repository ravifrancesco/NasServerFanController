# device records
import os


class DeviceRecord:

    def __init__(self):
        pass

    device_id = ""
    family = ""
    model = ""
    serial = ""
    firmware_version = ""
    capacity = ""
    sector_sizes = ""
    rotation_rate = ""
    device_is = ""
    ata_version = ""
    sata_version = ""
    smart_support_available = False
    smart_support_enabled = False


# HDD/SSD class
def run_smartctl(str_args):
    cmdstring = "smartctl " + str_args
    the_output = os.popen(cmdstring).read()
    lines = str.splitlines(the_output)
    # lines = ["/dev/sda"]
    return lines


class MassStorageDevice:
    dev = None
    device_id = None

    def __init__(self, device_id):
        self.device_id = device_id
        self.dev = self.get_device_info()

    def get_device_info(self):
        dev = DeviceRecord()
        dev_info_lines = run_smartctl("-i " + self.device_id)
        b_entered_info_section = False
        dev.device_id = self
        for line2 in dev_info_lines:
            if not b_entered_info_section:
                line2.split(" ", 2)
                # if (the_first_field[0].lower() == 'smartctl' ):
                #    print "SmartCtl Version is: " + the_first_field[1]
                if line2.lower() == "=== start of information section ===":
                    b_entered_info_section = True
            else:
                field = line2.split(":", 1)
                if field[0].lower() == "model family":
                    dev.family = field[1].strip()
                elif field[0].lower() == "device model":
                    dev.model = field[1].strip()
                elif field[0].lower() == "serial number":
                    dev.serial = field[1].strip()
                elif field[0].lower() == "firmware version":
                    dev.firmware_version = field[1].strip()
                elif field[0].lower() == "user capacity":
                    dev.capacity = field[1].strip()
                elif field[0].lower() == "sector sizes":
                    dev.sector_sizes = field[1].strip()
                elif field[0].lower() == "rotation rate":
                    dev.rotation_rate = field[1].strip()
                elif field[0].lower() == "device is":
                    dev.device_is = field[1].strip()
                elif field[0].lower() == "ata version is":
                    dev.ata_version = field[1].strip()
                elif field[0].lower() == "sata version is":
                    dev.sata_version = field[1].strip()
                elif field[0].lower() == "smart support is":
                    temp = field[1].strip().split(" ", 1)
                    # temp = string.split(field[1]," ",1)
                    str_temp = temp[0].strip().lower()
                    if str_temp == "available":
                        dev.smart_support_available = True
                    elif str_temp == "unavailable":
                        dev.smart_support_available = False
                        dev.smart_support_enabled = False
                    elif str_temp == "enabled":
                        dev.smart_support_enabled = True
                    elif str_temp == "disabled":
                        dev.smart_support_enabled = False
        return dev

    def get_temperature(self):
        global current_temp
        dev_info_lines = run_smartctl("-l scttemp " + self.device_id)
        current_temp = 0  # default value
        for line2 in dev_info_lines:
            line2.split(" ", 2)
            field = line2.split(":", 1)
            if field[0].lower() == "current temperature":
                current_temp = field[1].strip()
            # elif  (field[0].lower() == "device model" ):
            #    dev.model = field[1].strip()
            # elif  (field[0].lower() == "serial number" ):
            #    dev.serial = field[1].strip()
        return int(current_temp.split()[0])
