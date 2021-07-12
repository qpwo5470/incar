import serial
import time
import threading
import socket
import json


line = [] #라인 단위로 데이터 가져올 리스트 변수
acc = 0

port = '/dev/ttyUSB0' # 시리얼 포트
baud = 9600 # 시리얼 보드레이트(통신속도)


def socketthread():
    global acc

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.0.2", 9999))
            while True:
                data = {'accel': acc}
                sock.sendall(bytes(json.dumps(data), encoding="utf-8"))
                time.sleep(1/30)
        except [ConnectionRefusedError, ConnectionAbortedError]:
            pass


def serialthread(ser):
    global line
    global acc

    while True:
        for c in ser.read():
            if c == 10:
                text = ''.join(line).strip()
                if text.isnumeric():
                    acc = int(text)
                else:
                    print(text)
                del line[:]
            else:
                line.append(chr(c))


if __name__ == "__main__":
    ser = serial.Serial(port, baud, timeout=0)
    serial_thread = threading.Thread(target=serialthread, args=(ser,))
    serial_thread.start()
    socket_thread = threading.Thread(target=socketthread(), args=())
    socket_thread.start()
