import serial
import time
import threading
import socket
import json

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
    global acc
    global p_button
    global gear

    while True:
        line = ser.readline()
        text = ''.join(line).strip()
        print(text)
        try:
            if text[0] == 'A':
                text = text[1:]
                if text.isnumeric():
                    acc = int(text)
                else:
                    print(text)
            elif text[0] == 'D':
                text = text[1:]
                temp = text.split('/')
                p_button = int(temp[0])
                gear = temp[1]
        except:
            pass


if __name__ == "__main__":
    serA = serial.Serial(portA, baud, timeout=0)
    serial_threadA = threading.Thread(target=serialthread, args=(serA,))
    serial_threadA.start()
    socket_thread = threading.Thread(target=socketthread(), args=())
    socket_thread.start()
