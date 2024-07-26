# ds3231.py

from machine import I2C, Pin
import ustruct
import utime

# Set up I2C
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
DS3231_I2C_ADDR = 0x68

def ds3231_read(reg, nbytes=1):
    return i2c.readfrom_mem(DS3231_I2C_ADDR, reg, nbytes)

def ds3231_write(reg, data):
    i2c.writeto_mem(DS3231_I2C_ADDR, reg, data)

def set_alarm(timestamp):
    # Convert timestamp to datetime
    t = utime.localtime(timestamp)
    
    # Set Alarm 1 to trigger at the specific date and time
    ds3231_write(0x07, ustruct.pack('B', ((t[5] // 10) << 4) | (t[5] % 10)))  # Seconds
    ds3231_write(0x08, ustruct.pack('B', ((t[4] // 10) << 4) | (t[4] % 10)))  # Minutes
    ds3231_write(0x09, ustruct.pack('B', ((t[3] // 10) << 4) | (t[3] % 10)))  # Hours
    ds3231_write(0x0A, ustruct.pack('B', ((t[2] // 10) << 4) | (t[2] % 10)))  # Day of month
    
    # Enable Alarm 1
    control = ds3231_read(0x0E)[0]
    ds3231_write(0x0E, ustruct.pack('B', control | 0x05))  # Enable Alarm 1 interrupt

def get_alarm():
    # Read Alarm 1 registers
    seconds = int(((ds3231_read(0x07)[0] & 0x70) >> 4) * 10 + (ds3231_read(0x07)[0] & 0x0F))
    minutes = int(((ds3231_read(0x08)[0] & 0x70) >> 4) * 10 + (ds3231_read(0x08)[0] & 0x0F))
    hours = int(((ds3231_read(0x09)[0] & 0x30) >> 4) * 10 + (ds3231_read(0x09)[0] & 0x0F))
    day = int(((ds3231_read(0x0A)[0] & 0x30) >> 4) * 10 + (ds3231_read(0x0A)[0] & 0x0F))
    
    # Get current year and month (assuming they haven't changed)
    current_time = utime.localtime()
    year, month = current_time[0], current_time[1]
    
    # Create a timestamp
    alarm_time = utime.mktime((year, month, day, hours, minutes, seconds, 0, 0))
    return alarm_time