import time
import network
import socket
from machine import Pin, PWM
import _thread
import config

# Motor control setup with L293D
pwmPIN = 16
dir1Pin = 14
dir2Pin = 15

# Initialize motor control GPIO
speed_gp = Pin(pwmPIN, Pin.OUT)
dir1_gp = Pin(dir1Pin, Pin.OUT)
dir2_gp = Pin(dir2Pin, Pin.OUT)

# Global variables with lock for thread safety
run_time = 20
delay_time = 1209600
motor_lock = _thread.allocate_lock()
exit_flag = False
last_watering_time = 0

def motor_control():
    global run_time, delay_time, exit_flag, last_watering_time
    pwm = PWM(speed_gp)
    pwm.freq(50)
    while not exit_flag:
        with motor_lock:
            current_run_time = run_time
            current_delay_time = delay_time
        
        if current_run_time > 0:
            last_watering_time = time.time()  # Update last watering time
            # Forward direction
            print("Starting motor forward")
            dir1_gp.value(1)
            dir2_gp.value(0)
            pwm.duty_u16(65535)
            start_time = time.time()
            while time.time() - start_time < current_run_time and not exit_flag:
                time.sleep(0.1)
            pwm.duty_u16(0)
            
            # Reverse direction for 10 seconds
            print("Reversing motor")
            dir1_gp.value(0)
            dir2_gp.value(1)
            pwm.duty_u16(65535)
            start_time = time.time()
            while time.time() - start_time < 10 and not exit_flag:  # 10 seconds reverse
                time.sleep(0.1)
            pwm.duty_u16(0)
            
            # Stop motor
            dir1_gp.value(0)
            dir2_gp.value(0)
            print("Stopping motor")
        
        start_time = time.time()
        while time.time() - start_time < current_delay_time and not exit_flag:
            time.sleep(1)
    
    print("Motor control thread exiting")

def connect_wifi():
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
    return status[0]

def validate_input(value, min_value=1, max_value=None):
    try:
        int_value = int(value)
        if int_value < min_value:
            return min_value
        if max_value and int_value > max_value:
            return max_value
        return int_value
    except ValueError:
        return None

def calculate_time_remaining():
    global last_watering_time, delay_time
    current_time = time.time()
    elapsed_time = current_time - last_watering_time
    remaining_time = max(0, delay_time - elapsed_time)
    
    days, remainder = divmod(int(remaining_time), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}"

def main():
    global run_time, delay_time, exit_flag, last_watering_time
    
    ip = connect_wifi()
    
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('listening on', addr)
    
    motor_thread = _thread.start_new_thread(motor_control, ())
    
    try:
        while not exit_flag:
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            request_str = str(request)
            
            if "GET /?stop=true" in request_str:
                exit_flag = True
                response = "Shutting down..."
            else:
                run_time_index = request_str.find('/?run_time=')
                delay_time_index = request_str.find('&delay_time=')
                
                if run_time_index > -1 and delay_time_index > -1:
                    new_run_time = validate_input(request_str[run_time_index+11:delay_time_index])
                    new_delay_time = validate_input(request_str[delay_time_index+12:].split()[0])
                    
                    if new_run_time is not None and new_delay_time is not None:
                        with motor_lock:
                            run_time = new_run_time
                            delay_time = new_delay_time
                        print("Updated run time to {} seconds and delay time to {} seconds.".format(run_time, delay_time))
                
                time_remaining = calculate_time_remaining()
                response = """<!DOCTYPE html>
                <html>
                <head>
                    <title>Motor Control Panel</title>
                    <meta http-equiv="refresh" content="60">
                </head>
                <body>
                <h1>Motor Control Panel</h1>
                <h2>Time until next watering: {}</h2>
                <form action="/" method="GET">
                Run time (seconds): <input type="number" name="run_time" min="1" value="{}"><br>
                Delay time (seconds): <input type="number" name="delay_time" min="1" value="{}"><br>
                <input type="submit" value="Update">
                </form>
                <form action="/" method="GET">
                <input type="hidden" name="stop" value="true">
                <input type="submit" value="Stop Server">
                </form>
                </body>
                </html>
                """.format(time_remaining, run_time, delay_time)
            
            cl.send('HTTP/1.1 200 OK\n')
            cl.send('Content-Type: text/html\n')
            cl.send('Connection: close\n\n')
            cl.sendall(response)
            cl.close()
    
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
    finally:
        exit_flag = True
        print("Waiting for threads to finish...")
        time.sleep(2)  # Give threads time to exit
        s.close()
        print("Server stopped")

if __name__ == "__main__":
    main()