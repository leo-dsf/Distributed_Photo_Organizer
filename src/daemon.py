import os
import socket
import threading
from src.p2p import p2p
import imagehash
from PIL import Image

class Daemon:
    def __init__(self, address, nodeid = None):
        """Constructor"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, 10000))

        self.image_folder = (os.path.dirname(os.path.abspath(__file__))).removesuffix("src") + "node" + str(nodeid) + "/"
        self.images = {}
        self.image_name = ""
        self.REQ_MSG = "REQUEST_IMAGE"
        
        iThread = threading.Thread(target=self.sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        self.read_images()
        # self.print_images() # print all images in the node

        # recive connection
        while True:
            data = sock.recv(2048)
            if not data:
                print("No data received.")
                break
            if data[0:1] == b'\x11':
                self.update_peers(data[1:])
            elif data[0:1] == b'\x12':
                #print("Received image: " + str(data[1:], "utf-8"))
                self.update_hashes(data[1:])
            elif data[0:1] == b'\x13':
                #print("Received image: " + str(data[1:], "utf-8"))  
                self.image_name = str(data[1:], "utf-8")
            elif data[0:1] == b'\x14':
                print("Daemon.")
                #m = data[1:]
                #self.recv_img(sock, m)
            elif data.decode("utf-8").split(" ")[0] == self.REQ_MSG:
                print("Image requested on daemon!!")
                print("Received request for image: " + data.decode("utf-8").split(" ")[1])
                #send message
                #sock.send("hello".encode("utf-8"))
                self.send_img(data.decode("utf-8").split(" ")[1], sock)
            else:
                print(data.decode("utf-8"))
    
    # send msg
    def sendMsg(self, sock):
        sock.send("Connection created successfully.".encode("utf-8"))
    
    # update peers
    def update_peers(self, peerData):
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]
        #print(p2p.peers)
    
    # update hashes
    def update_hashes(self, hashData):
        while hashData:

            data = str(hashData, "utf-8")
            data = data.split(",")
            if len(data[-1].split(":")) == 2 and data[-1].split(":")[1]:
                data = data[:-1]
        #print(data)
        #for i in range(0, len(data)):
        #    img_hash = data[i].split(":")[0]
        #    file_name = data[i].split(":")[1]
        #p2p.images[img_hash] = file_name

    # recive image
    def recv_img(self, sock, m):
        file = open(self.image_name, "wb")
        while m:
            file.write(m)
            m = sock.recv(2048)
            if len(m) != 2048:
                print(len(m))
                break

        file.close()
        print('Done.')    

    # request image
    def req_img(self, sock, img_name):
        sock.send(bytes("REQUEST_IMAGE " + img_name, "utf-8"))

    # create a dictionary of hash images and images names
    def read_images(self):
        for filename in os.listdir(self.image_folder):
            if filename.endswith(".png") or filename.endswith(".jpg") or \
            filename.endswith(".jpeg") or filename.endswith(".bmp") or \
            filename.endswith(".gif") or '.jpg' in filename or  filename.endswith(".svg"): 
                img_hash = imagehash.average_hash(Image.open(self.image_folder+filename))
                if str(img_hash) not in self.images:
                    self.images[str(img_hash)] = filename
                else:
                    print("Duplicate image found: " + filename)
                    os.remove(self.image_folder + filename)
                    print("Deleted.")
    
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
    
    # send image
    def send_img(self, img_name, connection):
        # get image from img_name   
        # send img_hash to connection
        # check image for dict value instead of key
        if str(img_name) in self.images.values():
            # get key from value
            for key in self.images:
                if self.images[key] == str(img_name):
                    img_hash = key
                    break
            connection.send(b'\x13' + bytes(self.images[img_hash], "utf-8"))
            file = open(self.image_folder + self.images[img_hash], "rb")
            size = os.path.getsize(self.image_folder + self.images[img_hash])
            data = file.read(size)
            connection.sendall(b'\x14' + data)
            print("Image sent from daemon.")
            file.close()
        else:  
            #send no image found message
            connection.send("No image found on daemon.".encode("utf-8"))