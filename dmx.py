from DMXEnttecPro import Controller
from DMXEnttecPro.utils import get_port_by_serial_number, get_port_by_product_id
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import time

my_port = get_port_by_product_id(24577)
dmx = Controller(my_port, auto_submit=True)

light_map = {
    '/tail': [[(1, 0), (2, 0), (3, 1)], [(1, 1), (2, 0), (3, 1)], [(1, 1), (2, 0), (3, 0)], [(1, 0), (2, 1), (3, 1)]],
    # off stop tail tail_welcome / chan 1-4
    '/tail_turn': [[(4, 0), (5, 0)], [(4, 1), (5, 0)], [(4, 1), (5, 1)]],
    # off turn hazard
    '/eye': [[(9, 0), (11, 0)], [(9, 1), (11, 0)], [(9, 1), (11, 1)]],
    # off low high
    '/turn': [[(12, 0), (14, 0)], [(12, 1), (14, 0)], [(12, 1), (14, 1)]],
    # off turn hazard
    '/eyeline': [[(13, 0), (15, 0), (16, 0)], [(13, 1), (15, 0), (16, 1)], [(13, 1), (15, 1), (16, 1)],
                [(13, 0), (15, 1), (16, 1)]]}
# off bottom both welcome

f = open('timeline.txt')
lines = [[float(line.split('\t')[0]), [sig.split(' ') for sig in line.split('\t')[1].split(',')]] for line in [l.strip() for l in f.readlines()]]
print(lines)


def default_handler(address, *args):
    global light_map
    global lines
    print(args)
    if address == '/play' and args[0]:
        start_time = time.time()
        i = 0
        while True:
            now = lines[i]
            if time.time()-start_time > now[0]:
                print(now)
                for each in now[1]:
                    sig = light_map[f'/{each[0]}'][int(each[1])]
                    for s in sig:
                        dmx.set_channel(s[0], s[1] * 255)
                i += 1
                if i == len(lines):
                    break



dispatcher = Dispatcher()
dispatcher.set_default_handler(default_handler)

ip = "192.168.1.109"
port = 2055

server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever
