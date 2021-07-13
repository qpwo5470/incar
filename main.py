import serial
import time
import threading
import socket
import json


line = []
acc = 0
p_button = 0
gear = 'N'
data = {}

portA = '/dev/ttyUSB0'
portB = '/dev/ttyUSB1'
baud = 9600


def socketthread():
    global acc
    global p_button
    global gear
    global data

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.1.69", 9999))
            while True:
                data['accel'] = acc
                data['P'] = p_button
                data['gear'] = gear
                sock.sendall(bytes(json.dumps(data), encoding="utf-8"))
                time.sleep(1/15)
        except [ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, BrokenPipeError]:
            pass


def serialthread(ser):
    global line
    global acc
    global p_button
    global gear

    while True:
        for c in ser.read():
            if c == 10:
                text = ''.join(line).strip()
                if text[0] == 'A':
                    text = text[1:]
                    if text.isnumeric():
                        acc = int(text)
                    else:
                        print(text)
                    del line[:]
                elif text[0] == 'D':
                    text = text[1:]
                    temp = text.split('/')
                    p_button = int(temp[0])
                    gear = temp[1]
            else:
                line.append(chr(c))


if __name__ == "__main__":
    ser = serial.Serial(portA, baud, timeout=0)
    serial_thread = threading.Thread(target=serialthread, args=(ser,))
    serial_thread.start()
    ser = serial.Serial(portB, baud, timeout=0)
    serial_thread = threading.Thread(target=serialthread, args=(ser,))
    serial_thread.start()
    socket_thread = threading.Thread(target=socketthread(), args=())
    socket_thread.start()
