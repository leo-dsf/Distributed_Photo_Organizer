from random import randint
from src.p2p import p2p
import socket
import threading

class Client():
    def __init__(self, address):
        """Constructor"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, 10000))
        self.image_name = ""

        iThread = threading.Thread(target=self.sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        # recive data
        while True:
            data = sock.recv(2048)
            if not data:
                print("No data received")
                break
            if data[0:1] == b'\x11':
                self.update_peers(data[1:])
            elif data[0:1] == b'\x12':
                #print("Received image: " + str(data[1:], "utf-8"))
                self.update_hashes(data[1:])
            elif data[0:1] == b'\x13':
                print("Received image: " + str(data[1:], "utf-8"))  
                self.image_name = str(data[1:], "utf-8")
            elif data[0:1] == b'\x14':
                m = data[1:]
                self.recv_img(sock, data)
            else:
                print(data.decode("utf-8"))
    
    # send peers
    def sendMsg(self, sock):
        while True:
            sock.send(bytes(input("Enter message: "), "utf-8"))
    
    # update peers
    def update_peers(self, peerData):
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]
    
    # update hashes
    def update_hashes(self, hashData):
        while hashData:
            data = str(hashData, "utf-8")
            data = data.split(",")
            if len(data[-1].split(":")) == 2 and data[-1].split(":")[1]:
                data = data[:-1]
        print(data)

    # recive image
    def recv_img(self, sock, data):
        file = open(self.image_name, "wb")
        m = data[1:]
        while m:
            print(len(m))
            file.write(m)
            m = sock.recv(2048)
            if len(m) != 2048:
                break
        file.close()
        print('Done!')

    # request image
    def req_img(self, sock, img_name):
        sock.send(bytes("REQUEST_IMAGE " + img_name, "utf-8"))
    
    # print images 
    def print_images(self):
        # print all key from self.images
        c = 0 # counter
        for img_hash in self.images:
            print("Image " + "[" + str(c) + "]")
            print("-- Image Name: " + self.images[img_hash])
            print("-- Hash Code: " + img_hash)
            print("\n")
            c += 1

if __name__ == "__main__":
    try:
        # generate int 1 to 5
        random_int = randint(1, 5)
        peer = p2p.peers[0]
        client = Client(peer)
        # get host
        host = socket.gethostname()
        print("Host: " + host)
    except Exception as e:
        print("Error: " + e)