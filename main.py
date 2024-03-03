import time
import network
import socket
from machine import Pin, PWM
import _thread
import config

# Motor control setup with L293D
pwmPIN = 16  # PWM pin for speed control
dir1Pin = 14  # Direction pin 1
dir2Pin = 15  # Direction pin 2

# Initialize motor control GPIO
speed_gp = Pin(pwmPIN, Pin.OUT)
dir1_gp = Pin(dir1Pin, Pin.OUT)
dir2_gp = Pin(dir2Pin, Pin.OUT)

# Global variables for run time and delay time
run_time = 20  # Initial run time in seconds
delay_time = 1209600   # Initial delay time in seconds

def motor_control():
    global run_time, delay_time
    pwm = PWM(speed_gp)
    pwm.freq(50)  # Set frequency for PWM
    while True:
        if run_time > 0:
            dir1_gp.value(1)
            dir2_gp.value(0)
            pwm.duty_u16(65535)  # Full speed
            time.sleep(run_time)  # Run motor for the specified time
            pwm.duty_u16(0)  # Stop motor
            dir1_gp.value(0)
            dir2_gp.value(0)
        time.sleep(delay_time)  # Delay between runs

_thread.start_new_thread(motor_control, ())

# WiFi Connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.ssid, config.password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('IP:', status[0])

# Web Server Setup
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    request = cl.recv(1024)
    print("request:", request)
    request_str = str(request)

    # Parsing HTTP GET request
    run_time_index = request_str.find('/?run_time=') + 11
    delay_time_index = request_str.find('&delay_time=') + 12
    
    if run_time_index > 11:
        try:
            end_index = request_str.find('&', run_time_index)
            if end_index == -1: end_index = len(request_str)
            run_time = int(request_str[run_time_index:end_index])
            print(f"Updated run time to {run_time} seconds.")
        except ValueError:
            print("Invalid run time received")
    
    if delay_time_index > 12:
        try:
            end_index = request_str.find(' ', delay_time_index)
            delay_time = int(request_str[delay_time_index:end_index])
            print(f"Updated delay time to {delay_time} seconds.")
        except ValueError:
            print("Invalid delay time received")

    # HTML response with current run_time and delay_time
    response = f"""<!DOCTYPE html>
<html>
<head><title>Motor Control Panel</title></head>
<body>
<h1>Motor Control Panel</h1>
<form action="/" method="GET">
Run time (seconds): <input type="number" name="run_time" min="1" value="{run_time}"><br>
Delay time (seconds): <input type="number" name="delay_time" min="1" value="{delay_time}"><br>
<input type="submit" value="Update">
</form>
</body>
</html>
"""
    cl.send('HTTP/1.1 200 OK\n')
    cl.send('Content-Type: text/html\n')
    cl.send('Connection: close\n\n')
    cl.sendall(response)
    cl.close()
