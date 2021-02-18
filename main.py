from threading import Thread

import pigpio
import psutil
import time
import gpiozero

import classes

def get_device_ids():
    lines = classes.run_smartctl("--scan")
    device_list = []
    for line in lines:
        device_id = line.split(" ", 1)[0]
        device_list.append(device_id)
    return device_list


def remove_dupes(devices):
    newlist = []
    for device in devices:
        currentSerial = device.dev.serial
        present = False
        for item in newlist:
            if item.dev.serial == currentSerial:
                present = True
        if not present:
            newlist.append(device)
    return newlist


def remove_disabled_unsupported(devices):
    newlist = []
    for device in devices:
        if device.dev.smart_support_available and device.dev.smart_support_enabled:
            newlist.append(device)
    return newlist


def compute_device_fan_speed(devices):
    max_temp = 0
    # test
    if not devices:
        print("NOPE")
    # end test
    for device in devices:
        current_temp = device.get_temperature()
        print("Model: " + str(device.dev.model) + " TEMP: " + str(current_temp))
        if current_temp > max_temp:
            max_temp = current_temp

    if max_temp <= 30:
        return 0
    elif 30 < max_temp <= 45:
        return ((max_temp - 30) / 15) * 40
    elif 45 < max_temp <= 55:
        return ((max_temp - 45) / 10) * 60 + 40
    else:
        return 100


def compute_cpu_fan_speed(cpu):
    cpu_temp = cpu.temperature
    print("CPU temp: " + str(cpu_temp))  # test
    cpu_usage = psutil.cpu_percent()

    if cpu_temp <= 30:
        return 0
    elif 30 < cpu_temp <= 45:
        return ((cpu_temp - 30) / 15) * 25 + (cpu_usage / 100) * 75
    elif 45 < cpu_temp <= 60:
        return ((cpu_temp - 45) / 15) * 35 + 25 + (cpu_usage / 100) * 40
    elif 60 < cpu_temp <= 85:
        return ((cpu_temp - 60) / 25) * 40 + 60
    else:
        return 100


def fan_speed_control(list_of_devices):
    cpu = gpiozero.CPUTemperature()

    print("TEST THREAD")  # test
    pwm_frequency = 25000
    fan_pin = 12
    rpm_pin = 6
    threshold = 0
    sleep_time = 1  # s

    pi = pigpio.pi()

    pigpio.pi.set_PWM_range(pi, fan_pin, 100)
    pigpio.pi.set_PWM_frequency(pi, fan_pin, pwm_frequency)
    pigpio.pi.set_PWM_dutycycle(pi, fan_pin, 0)

    prec_duty_cicle = 0

    # main cicle
    while True:
        current_rpm = measure_rpm(rpm_pin, pi, sleep_time)
        cpu_fan_speed = compute_cpu_fan_speed(cpu)
        if len(list_of_devices) > 0:
            device_fan_speed = compute_device_fan_speed(list_of_devices)
            new_duty_cicle = max(cpu_fan_speed, device_fan_speed)
        else:
            new_duty_cicle = cpu_fan_speed
        print(
            "Current RPM: " + str(current_rpm) + " - Current Duty Cicle: " + str(
                prec_duty_cicle) + " - New Duty Cicle: " + str(new_duty_cicle))

        if abs(new_duty_cicle - prec_duty_cicle) > threshold:
            print("TEST THRESHOLD")
            pigpio.pi.set_PWM_dutycycle(pi, fan_pin, new_duty_cicle)
            prec_duty_cicle = new_duty_cicle

        time.sleep(sleep_time)


def measure_rpm(rpm_pin, pi, sleep_time):
    num_cicles = 3

    start = time.time()
    for impulse_count in range(num_cicles):
        pigpio.pi.wait_for_edge(pi, rpm_pin, pigpio.RISING_EDGE, sleep_time)
        print("TEST edge")

    duration = time.time() - start  # seconds to run for loop
    frequency = num_cicles / duration  # in Hz
    return int((frequency * 60) / 2)


def main():
    device_list = get_device_ids()

    if not device_list:
        print("No mass storage devices found.")

    list_of_devices = []

    for str_device in device_list:
        device = classes.MassStorageDevice(str_device)
        print("DEVICE FOUND: " + str_device + " - " + str(device.dev))
        list_of_devices.append(device)

    list_of_devices = remove_dupes(list_of_devices)
    list_of_devices = remove_disabled_unsupported(list_of_devices)

    # _thread.start_new_thread(fan_speed_control, (list_of_devices,))
    t = Thread(target=fan_speed_control, args=(list_of_devices,))
    t.start()


def stress_test():
    start_number = 1
    end_number = 1000000

    # Record the test start time
    start = time.time()

    # Create variable to store the prime numbers and a counter
    primes = []
    noPrimes = 0

    # Loop through each number, then through the factors to identify prime numbers
    for candidate_number in range(start_number, end_number, 1):
        found_prime = True
        for div_number in range(2, candidate_number):
            if candidate_number % div_number == 0:
                found_prime = False
                break
        if found_prime:
            primes.append(candidate_number)
            noPrimes += 1

    # Once all numbers have been searched, stop the timer
    end = round(time.time() - start, 2)

    # Display the results, uncomment the last to list the prime numbers found
    print('Find all primes up to: ' + str(end_number))
    print('Time elasped: ' + str(end) + ' seconds')
    print('Number of primes found ' + str(noPrimes))
    # print(primes)

# program
main()

#stress test
#stress_test()
