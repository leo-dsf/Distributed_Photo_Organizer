import argparse
from random import randint
import time
from src.daemon import Daemon
from src.server import Server
import sys
from src.p2p import p2p

def daemon(nodeid = None):
    while True:
        try:
            print("Connecting...")
            time.sleep(randint(1, 5))   
            for peer in p2p.peers:
                # if server exists, run daemon with success (server is the first node)
                try:
                    daemon = Daemon(peer, nodeid)
                except KeyboardInterrupt:
                    sys.exit(0)
                
                except Exception as e:
                    pass
                
                try:
                    server = Server(nodeid)
                except KeyboardInterrupt:
                    sys.exit(0)
                except Exception as e:
                    print("Server: ",e)
                    print("Couldn't start server.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    # args to recive from input
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodeid", type = int, default = None)
    args = parser.parse_args()
    # start daemons
    daemon(args.nodeid)