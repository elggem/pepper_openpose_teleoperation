import zmq
import time
import json

ctx = zmq.Context()
sock = ctx.socket(zmq.PUSH)
sock.bind("tcp://*:1234")

wp_dict = {
    "1": [
        0.00545066874474287,
        -0.016569457948207855,
        0.7130000591278076
    ],
    "2": [
        -0.12787652015686035,
        -0.0009210659191012383,
        0.6430000066757202
    ],
    "5": [
        0.1664714366197586,
        -0.029319584369659424,
        0.7980000376701355
    ],
    "6": [
        0.30849453806877136,
        -0.16002611815929413,
        0.6830000281333923
    ]
}

print("Starting loop...")
i = 1
while True:
    msg_json = json.dumps(wp_dict)  
    sock.send_string(msg_json)
    print("Sent json file... %i" % i)
    i += 1
    time.sleep(0.03)

sock.close()
ctx.term()

