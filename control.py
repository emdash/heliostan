#!/usr/bin/env python3

import sys
import tty
import termios
import serial

# import pysabertooth

# motors = pysabertooth.Sabertooth(
#     '/dev/ttyACM0',
#     baudrate=115200,
#     address=128,
#     timeout=1.0
# )

sabertooth = serial.Serial("/dev/ttyACM0", 115200)
print("m1: start up")

speed = 0
old_settings = None

def clamp(l, h, v): return max(l, min(h, v))

def increment():
    adjust_speed(+100)

def decrement():
    adjust_speed(-100)

def adjust_speed(increment):
    global speed
    speed = clamp(-2048, 2048, speed + increment)
    print(f"m1: {speed}", file=sabertooth)

def stop():
    global speed
    speed = 0
    print(f"m1: 0", file=sabertooth)
    print(f"m1: shut down", file=sabertooth)

# UI **********************************************************

def raw_mode():
    global old_settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)

def restore():
    global old_settings
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def getch():
    c = sys.stdin.read(1)
    if c == '\x1b':
        c = getch()

        if c != '[':
            raise Exception("Unhandled Escape Sequence")

        c = getch()
        if   c == 'A': return 'Up'
        elif c == 'B': return 'Down'
        else:          raise Exception("Unhandled Escape Sequence")
    else:
        return c

def cls():
    print("\033c")

def main():
    try:
        stop()
        raw_mode()
        c = None
        while True:
            cls()
            print(f"Current Speed: {speed}\r\nLast Key: {repr(c)}\r\n")
            c = getch()

            if   c == 'q':    return
            elif c == 'Up':   increment()
            elif c == 'Down': decrement()
            elif c == '\n':   stop()
            elif c == '\r':   stop()
            elif c == ' ':    stop()
            else:             pass
    finally:
        stop()
        restore()

if __name__ == "__main__":
    main()
