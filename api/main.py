import socket
import network
import utime
import ntptime
from machine import Pin, PWM
import json
import config
import os

# Constants
PORT = 8080
WATERING_DURATION_DEFAULT = 5  # Default 5 seconds
WATERING_DELAY_DEFAULT = 86400  # Default 1 day in seconds

# Motor control setup with L293D
pwmPIN = 16
dir1Pin = 14
dir2Pin = 15

# Initialize motor control GPIO
speed_gp = PWM(Pin(pwmPIN))
dir1_gp = Pin(dir1Pin, Pin.OUT)
dir2_gp = Pin(dir2Pin, Pin.OUT)
speed_gp.freq(50)  # Set PWM frequency to 50Hz

# Global variables
watering_duration = WATERING_DURATION_DEFAULT
watering_delay = WATERING_DELAY_DEFAULT
next_watering_time = None

def save_watering_time(timestamp):
    with open('watering_time.txt', 'w') as f:
        f.write(str(timestamp))

def load_watering_time():
    try:
        with open('watering_time.txt', 'r') as f:
            return int(f.read().strip())
    except OSError:
        return None  # File doesn't exist yet

def sync_time():
    try:
        ntptime.settime()
        print("Time synced with NTP server")
    except:
        print("Could not sync with NTP server")

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.ssid, config.password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        utime.sleep(1)
    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print('Device IP:', status[0])
    return status[0]

def run_motor(duration, reverse=False):
    if reverse:
        dir1_gp.value(0)
        dir2_gp.value(1)
    else:
        dir1_gp.value(1)
        dir2_gp.value(0)
    
    speed_gp.duty_u16(65535)  # Full speed
    utime.sleep(duration)
    
    # Stop motor
    speed_gp.duty_u16(0)
    dir1_gp.value(0)
    dir2_gp.value(0)
    
    return f'Motor ran {"in reverse " if reverse else ""}for {duration} seconds'

def get_time_remaining():
    current_time = utime.time()
    remaining = next_watering_time - current_time
    return max(0, remaining)  # Ensure we don't return negative values

def update_watering_schedule(duration, delay):
    global watering_duration, watering_delay, next_watering_time
    current_time = utime.time()
    
    watering_duration = duration
    watering_delay = int(delay * 86400)  # Convert days to seconds
    next_watering_time = current_time + watering_delay
    
    save_watering_time(next_watering_time)
    
    print(f"Current UTC: {current_time}, Next watering UTC: {next_watering_time}, Delay: {watering_delay}")
    
    return {
        "duration": watering_duration,
        "delay": watering_delay / 86400,  # Convert back to days for display
        "current_time": current_time,
        "next_watering": next_watering_time,
        "time_remaining": get_time_remaining()
    }

def handle_request(request):
    global watering_duration, watering_delay
    
    if isinstance(request, bytes):
        request = request.decode('utf-8')

    headers = (
        "HTTP/1.0 200 OK\r\n"
        "Content-type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        "\r\n"
    )

    if request.startswith('OPTIONS'):
        return headers.encode('utf-8')

    response_body = ""
    if 'POST /update_watering' in request:
        try:
            body_start = request.index('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            duration = data.get('duration', WATERING_DURATION_DEFAULT)
            delay = data.get('delay', WATERING_DELAY_DEFAULT / 86400)
            result = update_watering_schedule(duration, delay)
            response_body = json.dumps(result)
        except ValueError:
            response_body = json.dumps({'error': 'Invalid JSON'})
    elif 'GET /watering_info' in request:
        response_body = json.dumps({
            "duration": watering_duration,
            "delay": watering_delay / 86400,
            "time_remaining": get_time_remaining()
        })
    elif 'POST /start_motor' in request:
        response_body = json.dumps({"status": run_motor(watering_duration)})
    elif 'POST /stop_motor' in request:
        response_body = json.dumps({"status": "Motor stopped"})
        speed_gp.duty_u16(0)
        dir1_gp.value(0)
        dir2_gp.value(0)
    else:
        response_body = json.dumps({'error': 'Invalid endpoint'})
    
    return (headers + response_body).encode('utf-8')

def check_watering():
    global next_watering_time
    current_time = utime.time()
    if current_time >= next_watering_time:
        run_motor(watering_duration)
        next_watering_time = current_time + watering_delay
        save_watering_time(next_watering_time)

def main():
    global next_watering_time
    
    ip = connect_wifi()
    
    sync_time()
    
    next_watering_time = load_watering_time()
    current_time = utime.time()
    if next_watering_time is None or next_watering_time <= current_time:
        next_watering_time = current_time + watering_delay
        save_watering_time(next_watering_time)
    
    print(f"Current time after sync: {current_time}")
    print(f"Next watering time: {next_watering_time}")
    print(f"Time remaining: {get_time_remaining()}")
    
    addr = socket.getaddrinfo('0.0.0.0', PORT)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print(f'Listening on http://{ip}:{PORT}')
    
    while True:
        check_watering()
        
        s.setblocking(False)
        try:
            cl, addr = s.accept()
            print(f'Client connected from {addr}')
            cl.setblocking(False)
            request = b""
            while b"\r\n\r\n" not in request:
                try:
                    request += cl.recv(1024)
                except OSError:
                    pass
            response = handle_request(request)
            cl.send(response)
            cl.close()
        except OSError:
            pass
        
        utime.sleep(1)

if __name__ == '__main__':
    main()