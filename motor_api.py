import socket
import network
import utime
import ntptime
from machine import Pin, PWM, RTC
import json
import config

utime.sleep(2)  # Wait for 2 seconds before starting

PORT = 8080  # Choose an unused port

# Motor control setup with L293D
pwmPIN = 16
dir1Pin = 14
dir2Pin = 15

# Initialize motor control GPIO
speed_gp = PWM(Pin(pwmPIN))
dir1_gp = Pin(dir1Pin, Pin.OUT)
dir2_gp = Pin(dir2Pin, Pin.OUT)
speed_gp.freq(50)  # Set PWM frequency to 50Hz

# RTC setup
rtc = RTC()

# Watering schedule
watering_duration = 5  # Default 5 seconds
watering_delay = 86400  # Default 1 day in seconds
next_watering_time = utime.time() + watering_delay
last_sync_time = 0

# Sync time with NTP server after connecting to WiFi
def sync_time():
    try:
        ntptime.settime()
        print("Time synchronized with NTP server")
    except:
        print("Could not sync with NTP server")
        
def check_and_sync_time():
    global last_sync_time
    current_time = utime.time()
    if current_time - last_sync_time > 86400:  # 86400 seconds in a day
        sync_time()
        last_sync_time = current_time

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
    current_time = utime.time()  # Get current UTC time in seconds
    
    # Calculate how much time has passed since the last scheduled watering
    time_passed = max(0, current_time - (next_watering_time - watering_delay))
    
    # Update duration and delay
    watering_duration = duration
    new_delay = int(delay * 86400)  # Convert days to seconds
    
    # Calculate the new next_watering_time
    if time_passed >= new_delay:
        # If the new delay has already passed, schedule immediate watering
        next_watering_time = current_time
    else:
        # Adjust the next_watering_time based on the new delay and progress
        next_watering_time = (next_watering_time - watering_delay) + new_delay
    
    # Update the delay
    watering_delay = new_delay
    
    time_remaining = max(0, next_watering_time - current_time)
    
    print(f"Current UTC: {current_time}, Next watering UTC: {next_watering_time}, Delay: {watering_delay}, Time remaining: {time_remaining}")
    
    return {
        "duration": watering_duration,
        "delay": watering_delay / 86400,  # Convert back to days for display
        "current_time": current_time,
        "next_watering": next_watering_time,
        "time_remaining": time_remaining
    }


def handle_request(request):
    # Convert request to string if it's bytes
    if isinstance(request, bytes):
        request = request.decode('utf-8')

    # Prepare headers
    headers = (
        "HTTP/1.0 200 OK\r\n"
        "Content-type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        "\r\n"
    )

    # Handle CORS preflight request
    if request.startswith('OPTIONS'):
        return headers.encode('utf-8')

    response_body = ""
    if 'POST /update_watering' in request:
        try:
            body_start = request.index('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            duration = data.get('duration', 5)
            delay = data.get('delay', 1)
            result = update_watering_schedule(duration, delay)
            response_body = json.dumps(result)
            print(response_body)
        except ValueError:
            response_body = json.dumps({'error': 'Invalid JSON'})
    elif 'GET /watering_info' in request:
        response_body = json.dumps({
            "duration": watering_duration,
            "delay": watering_delay / 86400,
            "time_remaining": get_time_remaining()
        })
        print(response_body)
    elif 'POST /start_motor' in request:
        response_body = start_motor()
    elif 'POST /stop_motor' in request:
        response_body = stop_motor()
    else:
        response_body = json.dumps({'error': 'Invalid endpoint'})
    
    # Combine headers and body, then convert to bytes
    full_response = (headers + response_body).encode('utf-8')
    return full_response
    
def check_watering():
    global next_watering_time
    current_time = utime.time()
    if current_time >= next_watering_time:
        run_motor(watering_duration)
        next_watering_time = current_time + watering_delay
        
def start_motor():
    dir1_gp.value(1)
    dir2_gp.value(0)
    speed_gp.duty_u16(65535)  # Full speed
    return json.dumps({"status": "Motor started"})

def stop_motor():
    speed_gp.duty_u16(0)
    dir1_gp.value(0)
    dir2_gp.value(0)
    return json.dumps({"status": "Motor stopped"})

def main():
    ip = connect_wifi()
    
    sync_time()
    
    addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]  # Use port 8080
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print(f'Listening on http://{ip}:8080')
    
    while True:
        check_and_sync_time()
        check_watering()
        
        # Non-blocking socket accept
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