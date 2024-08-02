import socket
from machine import Pin, PWM
import network
import json
import utime
import config

# Motor control setup with L293D
pwmPIN = 16
dir1Pin = 14
dir2Pin = 15

# Initialize motor control GPIO
speed_gp = PWM(Pin(pwmPIN))
dir1_gp = Pin(dir1Pin, Pin.OUT)
dir2_gp = Pin(dir2Pin, Pin.OUT)

speed_gp.freq(50)  # Set PWM frequency to 50Hz

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

def handle_request(request):
    if 'POST /run_motor' in request:
        try:
            body_start = request.index('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            duration = data.get('duration', 1)
            message = run_motor(duration)
            return json.dumps({'message': message})
        except ValueError:
            return json.dumps({'error': 'Invalid JSON'})
    elif 'POST /run_motor_reverse' in request:
        try:
            body_start = request.index('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            duration = data.get('duration', 1)
            message = run_motor(duration, reverse=True)
            return json.dumps({'message': message})
        except ValueError:
            return json.dumps({'error': 'Invalid JSON'})
    else:
        return json.dumps({'error': 'Invalid endpoint'})

def main():
    ip = connect_wifi()
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print(f'Listening on http://{ip}:80')

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024).decode()
        response = handle_request(request)
        
        cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        cl.send(response)
        cl.close()

if __name__ == '__main__':
    main()