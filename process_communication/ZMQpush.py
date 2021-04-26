import zmq
import time
import json

class ZMQpush:
    ctx = None
    sock = None

    ## method init
    # 
    # class initialization 
    def __init__(self):
        # initialize socket
        ctx = zmq.Context()
        sock = ctx.socket(zmq.PUSH)

        # try socket bind
        try: 
            sock.bind("tcp://*:1234")
        except zmq.error.ZMQError as e:
            print(e)
            sys.exit(-1)
    
    ## method send
    #
    # convert dictionary to json and send it via tcp socket
    def send(self, msg_dict):
        msg_json = json.dumps(msg_dict)  
        sock.send_string(msg_json)

    ## method close
    # 
    # close socket
    def close(self):
        sock.close()
        ctx.term()