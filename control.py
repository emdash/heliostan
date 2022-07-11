#!/usr/bin/env python3

import sys
import tty
import termios
import serial

def debug(*args):
    print(args)
    return args[-1]

# Simulator *******************************************************************

class Simulator:

    def __init__(self):
        self.m1 = 0
        self.m2 = 0
        self.a1 = 512
        self.a2 = -1043
        self.m1_current = 31
        self.m2_current = 21
        self.batt = 127
        self.next_read = b""

    def write(self, line):
        line = line.strip()
        if   line == b"m1: get":  self.next_read = bytes(f"M1: {self.m1}", "utf8")
        elif line == b"m2: get":  self.next_read = bytes(f"M2: {self.m2}", "utf8")
        elif line == b"m1: getb": self.next_read = bytes(f"M1:B{self.batt}", "utf8")
        elif line == b"m2: getb": self.next_read = bytes(f"M2:B{self.batt}", "utf8")
        elif line == b"m1: getc": self.next_read = bytes(f"M1:C{self.m1_current}", "utf8")
        elif line == b"m2: getc": self.next_read = bytes(f"M2:C{self.m2_current}", "utf8")
        elif line == b"a1: get":  self.next_read = bytes(f"A1: {self.a1}", "utf8")
        elif line == b"a2: get":  self.next_read = bytes(f"A2: {self.a2}", "utf8")
        else:                     self.next_read = b""

    def readline(self):
        next_read = self.next_read
        self.next_read = b""
        return next_read + b"\r\n"
    

# Serial Protocol *************************************************************

if len(sys.argv) >= 2 and sys.argv[1] == "simulate":
    sabertooth = Simulator()
else:
    sabertooth = serial.Serial("/dev/ttyACM0", 115200)

speed = 0
old_settings = None

def clamp(l, h, v): return max(l, min(h, v))
def sprint(s):      sabertooth.write(bytes(s + "\n", "utf8"))
def sread():        return sabertooth.readline().decode("utf8")
def increment():    adjust_speed(+100)
def decrement():    adjust_speed(-100)

def adjust_speed(increment):
    global speed
    speed = clamp(-2048, 2048, speed + increment)
    sprint(f"m1: {speed}")

def stop():
    global speed
    speed = 0
    sprint(f"m1: 0")
    sprint(f"m1: shut down")

def start():
    global speed
    speed = 0
    sprint(f"m1: 0")
    sprint(f"m1: start up")

def query(cmd):
    sprint(cmd)
    return sread().strip()

def get_battery():
    response = query("m1: getb")
    return float(response.lstrip("M1:B")) / 10.0

def get_current():
    response = query("m1: getc")
    return float(response.lstrip("M1:C")) / 10.0

def get_a1():
    response = query("a1: get")
    return float(response.lstrip("A1: "))

def get_a2():
    response = query("a2: get")
    return float(response.lstrip("A2: "))
    
# UI **************************************************************************

def setup():
    global old_settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)

    new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)
    new_settings[6][termios.VMIN] = 0
    new_settings[6][termios.VTIME] = 2

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)

def restore():
    global old_settings
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def getch():
    c = sys.stdin.read(1)

    if not c:
        raise IOError("Timeout")
    elif c == '\x1b':
        c = sys.stdin.read(1)
        if c != '[':   raise Exception("Unhandled Escape Sequence: {c}")

        c = sys.stdin.read(1)
        if   c == 'A': return 'Up'
        elif c == 'B': return 'Down'
        else:          raise Exception("Unhandled Escape Sequence: {c}")
    else:
        return c

def cls(): sys.stdout.write("\033c")

def idle_queries():
    return {
        "batt":    get_battery(),
        "current": get_current(),
        "a1":      get_a1(),
        "a2":      get_a2()
    }

def main():
    try:
        stop()
        setup()
        c = None
        data = idle_queries()
        while True:
            cls()
            print(f"Current Speed:   {speed}\r\n"
                  f"Last Key:        {repr(c)}\r\n"
                  f"Battery Voltage: {data['batt']}\r\n"
                  f"Motor Current:   {data['current']}\r\n"
                  f"Analog 1:        {data['a1']}\r\n"
                  f"Analog 2:        {data['a2']}\r\n")
            try:
                c = getch()
            except IOError:
                data = idle_queries()
                continue

            if   c == 'q':    return
            elif c == 'Up':   increment()
            elif c == 'Down': decrement()
            elif c == '\t':   start()
            elif c == '\n':   stop()
            elif c == '\r':   stop()
            elif c == ' ':    stop()
            else:             pass
    finally:
        stop()
        restore()

if __name__ == "__main__":
    main()
